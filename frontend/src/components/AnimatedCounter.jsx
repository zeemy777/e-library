
import { useEffect, useRef, useState } from "react";

function prefersReducedMotion() {
  return typeof window !== "undefined"
    && window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
}

// Counts up from zero the first time it becomes visible.
function AnimatedCounter({ value, duration = 1100 }) {

  const [animated, setAnimated] = useState(0);
  const ref = useRef(null);
  const frameRef = useRef(0);
  const startRef = useRef(0);
  const reduceMotion = prefersReducedMotion();

  useEffect(() => {

    const element = ref.current;

    if (!element || reduceMotion) {
      return undefined;
    }

    function step(timestamp) {

      if (!startRef.current) {
        startRef.current = timestamp;
      }

      const progress = Math.min(
        (timestamp - startRef.current) / duration,
        1
      );

      // Ease-out so the number settles gently.
      const eased = 1 - Math.pow(1 - progress, 3);

      setAnimated(Math.round(value * eased));

      if (progress < 1) {
        frameRef.current = requestAnimationFrame(step);
      }
    }

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          frameRef.current = requestAnimationFrame(step);
          observer.disconnect();
        }
      },
      { threshold: 0.4 }
    );

    observer.observe(element);

    return () => {
      observer.disconnect();
      cancelAnimationFrame(frameRef.current);
    };
  }, [value, duration, reduceMotion]);

  // Show the final value immediately when the visitor asks for less motion.
  return <span ref={ref}>{reduceMotion ? value : animated}</span>;
}

export default AnimatedCounter;
