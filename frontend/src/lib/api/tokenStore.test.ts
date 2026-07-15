import { clearAccessToken, getAccessToken, setAccessToken } from './tokenStore'

describe('access token em memoria', () => {
  it('guarda, le e limpa o token', () => {
    setAccessToken('access-test')
    expect(getAccessToken()).toBe('access-test')
    clearAccessToken()
    expect(getAccessToken()).toBeNull()
  })

  it('nao usa localStorage nem sessionStorage', () => {
    const localSpy = vi.spyOn(Storage.prototype, 'setItem')
    setAccessToken('memory-only')
    expect(localSpy).not.toHaveBeenCalled()
    expect(localStorage.getItem('access')).toBeNull()
    expect(sessionStorage.getItem('access')).toBeNull()
  })
})
