let cached = null

/** Fetches the real DLVC logo and returns the raw PNG base64 payload (no data: prefix). */
export async function getLogoPngBase64() {
  if (cached) return cached
  const buf = await fetch('/images/logo-dlvc.png').then(r => r.arrayBuffer())
  let binary = ''
  const bytes = new Uint8Array(buf)
  const chunk = 0x8000
  for (let i = 0; i < bytes.length; i += chunk) {
    binary += String.fromCharCode.apply(null, bytes.subarray(i, i + chunk))
  }
  cached = btoa(binary)
  return cached
}
