import env from '../config/env';
import { NudgeService } from './NudgeService';

class RealtimeService {
  private controller: AbortController | null = null;
  private isConnected: boolean = false;

  async start(token: string) {
    if (this.isConnected) return;
    
    console.log('[RealtimeService] Starting nudge stream...');
    this.controller = new AbortController();
    this.isConnected = true;

    try {
      const response = await fetch(`${env.API_URL}/api/notifications/stream`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'text/event-stream',
        },
        signal: this.controller.signal,
      });

      if (!response.body) {
        throw new Error('No response body for SSE');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.replace('data: ', '').trim();
            if (dataStr) {
              try {
                const nudge = JSON.parse(dataStr);
                console.log('[RealtimeService] Received nudge:', nudge);
                NudgeService.show(nudge.message, nudge.type || 'reminder');
              } catch (e) {
                console.error('[RealtimeService] Failed to parse nudge data:', e);
              }
            }
          }
        }
      }
    } catch (error: any) {
      if (error.name === 'AbortError') {
        console.log('[RealtimeService] Stream aborted');
      } else {
        console.error('[RealtimeService] Stream error:', error);
        // Reconnect after delay
        this.isConnected = false;
        setTimeout(() => this.start(token), 5000);
      }
    } finally {
      this.isConnected = false;
    }
  }

  stop() {
    if (this.controller) {
      this.controller.abort();
      this.controller = null;
    }
    this.isConnected = false;
  }
}

export const realtimeService = new RealtimeService();
