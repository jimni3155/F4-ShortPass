export function useTTS() {
  const audioRef = useRef(new Audio());
  const ttsEndCallbacks = useRef([]);

  const speak = async (text) => {
    const res = await fetch('/api/tts', {});
  };
}
