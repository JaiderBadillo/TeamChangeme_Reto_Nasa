import { handleReading } from '../server/readings.mjs'

export default (request, response) => handleReading('export', request, response)
