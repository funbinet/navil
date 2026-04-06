export class ScanSocket {
  constructor(scanId, onEvent) {
    this.scanId = scanId;
    this.onEvent = onEvent;
    this.socket = null;
    this.retry = 0;
  }

  connect() {
    if (!this.scanId) {
      return;
    }
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    this.socket = new WebSocket(`${protocol}://${window.location.host}/ws/scan/${this.scanId}`);

    this.socket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        this.onEvent(payload);
      } catch {
        this.onEvent({ type: "raw", message: event.data });
      }
    };

    this.socket.onclose = () => {
      if (this.retry > 6) {
        return;
      }
      this.retry += 1;
      window.setTimeout(() => this.connect(), this.retry * 700);
    };
  }

  close() {
    if (this.socket) {
      this.socket.close();
    }
  }
}
