// 管理画面の編集ページにAIレビューのボタンを差し込む
document.addEventListener("DOMContentLoaded", () => {
  const findPageId = (form) => {
    const hidden = form?.querySelector("input[name=page_id]") || document.querySelector("input[name=page_id]");
    if (hidden && hidden.value) return hidden.value;
    // URL (/admin/pages/<id>/edit/) から拾うフォールバック
    const match = location.pathname.match(/\/admin\/pages\/(\d+)\/edit\/?/);
    return match ? match[1] : null;
  };

  const mountButton = () => {
    const form =
      document.querySelector("form#page-edit-form") ||
      document.querySelector("form[action*='/edit/']") ||
      document.querySelector("main form") ||
      document.querySelector("form");
    if (!form) return false;

    const csrfInput = form.querySelector("input[name=csrfmiddlewaretoken]") || document.querySelector("input[name=csrfmiddlewaretoken]");
    const pageId = findPageId(form);
    if (!pageId || !csrfInput) return false;

    // 既に設置済みならスキップ
    const existingButton = document.querySelector("[data-draft-review-button]") || form.querySelector(".draft-review-button");
    if (existingButton) {
      attachBehavior(existingButton, pageId, csrfInput);
      return true;
    }

    const actions =
      document.querySelector("[data-w-action-buttons]") ||
      document.querySelector("[data-wagtail-action-buttons]") ||
      document.querySelector("[data-controller='w-action-buttons']") ||
      document.querySelector(".w-header__actions") ||
      document.querySelector(".header-actions") ||
      document.querySelector(".action-buttons") ||
      form.querySelector(".actions") ||
      form;
    if (!actions) return false;

    const reviewButton = document.createElement("button");
    reviewButton.type = "button";
    reviewButton.className = "button button-secondary draft-review-button";
    reviewButton.textContent = "下書きをAIレビュー";
    reviewButton.setAttribute("data-draft-review-button", pageId);
    actions.appendChild(reviewButton);

    attachBehavior(reviewButton, pageId, csrfInput);
    return true;
  };

  const attachBehavior = (button, pageId, csrfInput) => {
    if (button.dataset.draftReviewBound === "1") return;
    button.dataset.draftReviewBound = "1";

    let modal = document.querySelector(".draft-review-modal");
    if (!modal) {
      modal = document.createElement("div");
      modal.className = "draft-review-modal";
      modal.innerHTML = `
        <div class="draft-review-modal__backdrop"></div>
        <div class="draft-review-modal__content">
          <div class="draft-review-modal__header">AIレビュー</div>
          <div class="draft-review-modal__body">ここに改善案が表示されます</div>
          <div class="draft-review-modal__footer">
            <button type="button" class="button button-secondary fetch-btn">改善案を取得</button>
            <button type="button" class="button close-btn">閉じる</button>
          </div>
        </div>`;
      document.body.appendChild(modal);

      const content = modal.querySelector(".draft-review-modal__content");
      const header = modal.querySelector(".draft-review-modal__header");
      const closeModal = () => modal.classList.remove("is-open");
      modal.querySelector(".close-btn").addEventListener("click", closeModal);

      // ドラッグで移動
      let isDragging = false;
      let startX = 0;
      let startY = 0;
      let startLeft = 0;
      let startTop = 0;
      header.addEventListener("mousedown", (ev) => {
        isDragging = true;
        startX = ev.clientX;
        startY = ev.clientY;
        const rect = content.getBoundingClientRect();
        startLeft = rect.left;
        startTop = rect.top;
        content.classList.add("is-dragging");
      });
      document.addEventListener("mousemove", (ev) => {
        if (!isDragging) return;
        const dx = ev.clientX - startX;
        const dy = ev.clientY - startY;
        content.style.left = `${startLeft + dx}px`;
        content.style.top = `${startTop + dy}px`;
        content.style.transform = "none";
      });
      document.addEventListener("mouseup", () => {
        if (isDragging) {
          isDragging = false;
          content.classList.remove("is-dragging");
        }
      });
    }

    const openModal = (contentText) => {
      modal.querySelector(".draft-review-modal__body").textContent = contentText;
      const contentEl = modal.querySelector(".draft-review-modal__content");
      // 位置をセンターへリセット
      contentEl.style.left = "50%";
      contentEl.style.top = "50%";
      contentEl.style.transform = "translate(-50%, -50%)";
      modal.classList.add("is-open");
    };

    const fetchButton = modal.querySelector(".fetch-btn");
    fetchButton.addEventListener("click", async () => {
      openModal("送信中...");
      try {
        const response = await fetch(`/admin/api/draft-review/${pageId}/`, {
          method: "POST",
          headers: {
            "X-CSRFToken": csrfInput.value,
            "Content-Type": "application/json",
          },
        });

        const data = await response.json();
        if (!response.ok) {
          openModal(data.error || "レビュー取得に失敗しました");
          return;
        }
        openModal(data.review || "改善案が空でした");
      } catch (err) {
        openModal(`エラー: ${err}`);
      }
    });

    button.addEventListener("click", (e) => {
      e.preventDefault();
      openModal("ここに改善案が表示されます");
    });
  };

  // 初回トライ
  if (mountButton()) return;

  // SPA遷移に対応するため監視
  const observer = new MutationObserver(() => {
    if (mountButton()) observer.disconnect();
  });
  observer.observe(document.body, { childList: true, subtree: true });
});

// 簡易スタイル（Wagtail管理画面と衝突しないよう名前空間を付与）
const style = document.createElement("style");
style.textContent = `
.draft-review-modal {
  display: none;
  position: fixed;
  inset: 0;
  z-index: 2000;
  pointer-events: none; /* 下のページ操作をブロックしない */
}
.draft-review-modal.is-open { display: block; }
.draft-review-modal__backdrop {
  position: absolute;
  inset: 0;
  background: transparent;
  pointer-events: none;
}
.draft-review-modal__content {
    position: absolute;
  top: 15%;
  left: 50%;
  transform: translate(-50%, 0);
  background: #fff;
  border-radius: 10px;
  padding: 0 16px 16px;
  width: min(360px, 90vw);
  height: min(80vh, 760px);
  min-width: 280px;
  min-height: 320px;
  overflow: auto;
  resize: both;
  box-shadow: 0 18px 36px rgba(0,0,0,0.28);
  border: 1px solid #d7d7d7;
  cursor: default;
  pointer-events: auto; /* ウィンドウ内は操作可 */
}
.draft-review-modal__content.is-dragging { opacity: 0.92; }
.draft-review-modal__header {
  font-weight: 700;
  margin: 0 -16px 12px;
  padding: 12px 16px;
  cursor: move;
  user-select: none;
  background: linear-gradient(90deg, #f2f4f8, #ffffff);
  border-bottom: 1px solid #e5e5e5;
  border-radius: 10px 10px 0 0;
}
.draft-review-modal__body {
  white-space: pre-wrap;
  line-height: 1.6;
  margin: 12px 0 16px;
}
.draft-review-modal__footer {
  text-align: right;
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}
`;
document.head.appendChild(style);
