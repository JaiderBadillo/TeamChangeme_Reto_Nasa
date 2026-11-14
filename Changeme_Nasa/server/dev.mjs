import { createServer } from 'node:http'
import experiment from '../api/experiment.js'
import series from '../api/series.js'
import catalog from '../api/catalog.js'
import download from '../api/export.js'

const handlers = new Map([['/api/experiment', experiment], ['/api/series', series], ['/api/catalog', catalog]])
handlers.set('/api/export', download)
createServer((request, response) => {
  const handler = handlers.get(new URL(request.url, 'http://localhost').pathname)
  if (handler) return handler(request, response)
  response.writeHead(404).end()
}).listen(8787, '127.0.0.1', () => console.log('CombusLab API on http://127.0.0.1:8787'))
