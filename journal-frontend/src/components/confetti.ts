import confetti from "canvas-confetti"

export function fireConfetti() {
  confetti({
    particleCount: 90,
    spread: 60,
    origin: { y: 0.6 }
  })
}
