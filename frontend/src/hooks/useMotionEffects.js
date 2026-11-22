
import { useEffect } from "react";

const RIPPLE_TARGETS = [
  ".primary-button",
  ".secondary-button",
  ".category-button",
  ".type-button",
  ".borrow-button"
].join(", ");

const TILT_TARGETS = ".book-card, .hero-visual";

// Document-level listeners for the scroll progress bar, hero spotlight,
// card tilt and button ripples, so any matching element gets them.
function useMotionEffects() {

  useEffect(() => {

    const root = document.documentElement;
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    const finePointer = window.matchMedia("(hover: hover) and (pointer: fine)");
    let frame = 0;

    const updateProgress = () => {
      frame = 0;
      const scrollable = root.scrollHeight - window.innerHeight;
      const progress = scrollable > 0 ? window.scrollY / scrollable : 0;
      root.style.setProperty("--scroll-progress", progress.toFixed(4));
    };

    const onScroll = () => {
      if (!frame) {
        frame = window.requestAnimationFrame(updateProgress);
      }
    };

    const onPointerMove = (event) => {
      if (reduceMotion.matches || !finePointer.matches) {
        return;
      }

      const hero = event.target.closest?.(".hero");

      if (hero) {
        const rect = hero.getBoundingClientRect();
        hero.style.setProperty("--hx", `${event.clientX - rect.left}px`);
        hero.style.setProperty("--hy", `${event.clientY - rect.top}px`);
        hero.classList.add("is-lit");
      }

      const card = event.target.closest?.(TILT_TARGETS);

      if (card) {
        const rect = card.getBoundingClientRect();
        const x = (event.clientX - rect.left) / rect.width;
        const y = (event.clientY - rect.top) / rect.height;

        card.style.setProperty("--rx", `${((0.5 - y) * 9).toFixed(2)}deg`);
        card.style.setProperty("--ry", `${((x - 0.5) * 11).toFixed(2)}deg`);
        card.style.setProperty("--mx", `${(x * 100).toFixed(1)}%`);
        card.style.setProperty("--my", `${(y * 100).toFixed(1)}%`);
        card.classList.add("is-tilting");
      }
    };

    const onPointerOut = (event) => {
      const next = event.relatedTarget;
      const card = event.target.closest?.(TILT_TARGETS);
      const hero = event.target.closest?.(".hero");

      if (card && !card.contains(next)) {
        card.classList.remove("is-tilting");
      }

      if (hero && !hero.contains(next)) {
        hero.classList.remove("is-lit");
      }
    };

    const onPointerDown = (event) => {
      if (reduceMotion.matches) {
        return;
      }

      const button = event.target.closest?.(RIPPLE_TARGETS);

      if (!button || button.disabled) {
        return;
      }

      const rect = button.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height) * 2.2;
      const ripple = document.createElement("span");

      ripple.className = "ripple";
      ripple.style.width = `${size}px`;
      ripple.style.height = `${size}px`;
      ripple.style.left = `${event.clientX - rect.left - size / 2}px`;
      ripple.style.top = `${event.clientY - rect.top - size / 2}px`;
      ripple.addEventListener("animationend", () => ripple.remove());

      button.appendChild(ripple);
    };

    updateProgress();

    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    document.addEventListener("pointermove", onPointerMove, { passive: true });
    document.addEventListener("pointerout", onPointerOut);
    document.addEventListener("pointerdown", onPointerDown);

    return () => {
      window.cancelAnimationFrame(frame);
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
      document.removeEventListener("pointermove", onPointerMove);
      document.removeEventListener("pointerout", onPointerOut);
      document.removeEventListener("pointerdown", onPointerDown);
    };
  }, []);
}

export default useMotionEffects;
