document.addEventListener("DOMContentLoaded", () => {
    const buttons = Array.from(document.querySelectorAll("[data-tab-target]"));
    const panels = Array.from(document.querySelectorAll("[data-tab-panel]"));

    buttons.forEach((button) => {
        button.addEventListener("click", () => {
            const target = button.dataset.tabTarget;

            buttons.forEach((item) => {
                const isActive = item === button;
                item.classList.toggle("is-active", isActive);
                item.setAttribute("aria-selected", String(isActive));
            });

            panels.forEach((panel) => {
                const isActive = panel.dataset.tabPanel === target;
                panel.classList.toggle("is-active", isActive);
                panel.hidden = !isActive;
            });
        });
    });

    const toast = document.querySelector("[data-toast-modal]");
    if (toast) {
        toast.addEventListener("animationend", (event) => {
            if (event.target !== toast || event.animationName !== "toast-fade") {
                return;
            }
            toast.remove();
        });
    }

    document.querySelectorAll("[data-amount-entry]").forEach((entry) => {
        const input = entry.querySelector("input");
        const keypadButtons = entry.querySelectorAll("[data-amount-key]");

        keypadButtons.forEach((keyButton) => {
            keyButton.addEventListener("click", () => {
                const key = keyButton.dataset.amountKey;
                const currentValue = input.value || "";

                if (key === "clear") {
                    input.value = "";
                } else if (key === "backspace") {
                    input.value = currentValue.slice(0, -1);
                } else if (currentValue.length < 7) {
                    const rawValue = `${currentValue}${key}`;
                    const nextValue = rawValue.replace(/^0+(?=\d)/, "") || "0";
                    input.value = nextValue.slice(0, 7);
                }

                input.dispatchEvent(new Event("input", { bubbles: true }));
            });
        });
    });
});
