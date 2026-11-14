import pg from 'pg'

let pool

export async function readSnapshot(operation) {
  if (!pool) {
    const { COMBUSLAB_DB_HOST: host, COMBUSLAB_DB_USER: user,
      COMBUSLAB_DB_PASSWORD: password, COMBUSLAB_DB_CA: ca } = process.env
    if (!host || !user || !password || !ca) throw new Error('Database configuration is incomplete')
    pool = new pg.Pool({
      host, user, password, database: 'postgres', port: 5432,
      ssl: { ca, rejectUnauthorized: true },
      max: 2, connectionTimeoutMillis: 5000, idleTimeoutMillis: 10000,
    })
    pool.on('error', () => console.error('Idle database connection closed'))
  }
  const client = await pool.connect()
  let discard = false
  const onConnectionError = () => { discard = true }
  client.on('error', onConnectionError)
  try {
    await client.query('BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY')
    await client.query("SET LOCAL statement_timeout = '5s'")
    const result = await operation(client)
    await client.query('COMMIT')
    return result
  } catch (error) {
    try { await client.query('ROLLBACK') } catch { discard = true }
    throw error
  } finally {
    client.removeListener('error', onConnectionError)
    client.release(discard)
  }
}
