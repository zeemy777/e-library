
import { useEffect, useRef, useState } from "react";

// Counts up from zero the first time it becomes visible.
function AnimatedCounter({ value, duration = 1100 }) {

  const [display, setDisplay] = useState(0);
  const ref = useRef(null);

  useEffect(() => {

    const element = ref.current;

    if (!element) {
      return undefined;
    }

    let frame = 0;
    let start = 0;

    function step(timestamp) {

      if (!start) {
        start = timestamp;
      }

      const progress = Math.min(
        (timestamp - start) / duration,
        1
      );

      // Ease-out so the number settles gently.
      const eased = 1 - Math.pow(1 - progress, 3);

      setDisplay(Math.round(value * eased));

      if (progress < 1) {
        frame = requestAnimationFrame(step);
      }
    }

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          frame = requestAnimationFrame(step);
          observer.disconnect();
        }
      },
      { threshold: 0.4 }
    );

    observer.observe(element);

    return () => {
      observer.disconnect();
      cancelAnimationFrame(frame);
    };
  }, [value, duration]);

  return <span ref={ref}>{display}</span>;
}

export default AnimatedCounter;
