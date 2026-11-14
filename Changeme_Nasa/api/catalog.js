import { handleReading } from '../server/readings.mjs'

export default (request, response) => handleReading('catalog', request, response)
