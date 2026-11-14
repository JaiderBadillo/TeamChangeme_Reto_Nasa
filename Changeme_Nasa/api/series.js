import { handleReading } from '../server/readings.mjs'

export default (request, response) => handleReading('series', request, response)
