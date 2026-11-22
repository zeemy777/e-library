
import { useEffect } from "react";

// Reveal elements marked with .reveal as they scroll into view.
// Running after every render picks up newly loaded cards and pages.
function useReveal() {

  useEffect(() => {

    const targets = document.querySelectorAll(
      ".reveal:not(.is-visible)"
    );

    if (!targets.length) {
      return undefined;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      {
        threshold: 0.08,
        rootMargin: "0px 0px -35px 0px"
      }
    );

    targets.forEach((target) => observer.observe(target));

    return () => observer.disconnect();
  });
}

export default useReveal;
