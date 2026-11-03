// Periodic refresh that can't leak.
//
// Call this.poll(fn, ms) from created(), before any await: the timer is
// registered immediately, so leaving the page while the first request is still
// running still stops it. Errors thrown by fn are caught (a backend that's down
// would otherwise produce an unhandled rejection on every tick) and passed to
// the component's optional onPollError(error) method.
export default {
  data() {
    return {
      pollTimers: []
    }
  },
  unmounted() {
    this.pollTimers.forEach(clearInterval)
    this.pollTimers = []
  },
  methods: {
    poll(fn, ms) {
      const timer = setInterval(async () => {
        try {
          await fn()
        } catch (error) {
          this.onPollError?.(error)
        }
      }, ms)
      this.pollTimers.push(timer)
    }
  }
}
