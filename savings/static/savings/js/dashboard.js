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
});
