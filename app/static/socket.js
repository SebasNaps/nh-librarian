
export const socket = io({
    transports: ['websocket', 'polling'],
    transportOptions: {
    polling: {
      extraHeaders: {},        // if you need any
      maxHttpBufferSize: 100000000
    },
    websocket: {
      // if you ever send big messages over the WS transport:
      maxFrameSize: 100000000
    }
  }
});

// export const socket = io();