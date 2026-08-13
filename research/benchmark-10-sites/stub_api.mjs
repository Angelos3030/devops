// Stub ΜΟΝΟ της βάσης, όχι της λογικής: σερβίρει το ίδιο JSON που θα επέστρεφε
// το `GET /clients/{id}/site-data` του src/meta_oauth.py, από τα αρχεία που
// παρήγαγε το generate.py μέσω του πραγματικού pipeline.
import { createServer } from 'node:http'
import { readFile } from 'node:fs/promises'

const DIR = new URL('../../sites/artifacts/benchmark/', import.meta.url)

createServer(async (req, res) => {
  const m = req.url.match(/^\/clients\/([^/?]+)\/site-data/)
  if (!m) { res.writeHead(404).end('{}'); return }
  try {
    const body = await readFile(new URL(`${decodeURIComponent(m[1])}.json`, DIR), 'utf8')
    res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' }).end(body)
  } catch {
    res.writeHead(404, { 'Content-Type': 'application/json' }).end('{"error":"not found"}')
  }
}).listen(3990, '127.0.0.1', () => console.log('stub site-data API → http://127.0.0.1:3990'))
