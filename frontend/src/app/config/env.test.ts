import { loadAppConfig } from './env'

describe('configuracao da aplicacao', () => {
  it('aceita e normaliza a URL da API', () => {
    expect(loadAppConfig({ VITE_API_BASE_URL: 'http://localhost:8000/api/v1/' })).toEqual({
      apiBaseUrl: 'http://localhost:8000/api/v1',
    })
  })

  it.each([undefined, 'ftp://example.com/api/v1', 'https://example.com/api'])('rejeita URL ausente ou invalida: %s', (value) => {
    expect(() => loadAppConfig({ VITE_API_BASE_URL: value })).toThrow()
  })
})
