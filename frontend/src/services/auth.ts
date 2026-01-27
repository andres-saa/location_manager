import axios from 'axios'
import type { TokenResponse } from '../stores/auth'

const VALIDATE_TOKEN_URL = 'https://backend.salchimonster.com/validate-token'

export async function validateToken(token: string): Promise<TokenResponse | null> {
  try {
    // Intentar primero con el token en el header Authorization
    const response = await axios.post<TokenResponse>(
      VALIDATE_TOKEN_URL,
      {},
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      }
    )

    return response.data
  } catch (error) {
    // Si falla con Authorization header, intentar con query parameter
    if (axios.isAxiosError(error) && (error.response?.status === 401 || error.response?.status === 403)) {
      try {
        const response = await axios.post<TokenResponse>(
          `${VALIDATE_TOKEN_URL}?token=${encodeURIComponent(token)}`,
          {},
          {
            headers: {
              'Content-Type': 'application/json',
            },
          }
        )
        return response.data
      } catch (secondError) {
        console.error('Error validando token (segundo intento):', secondError)
        return null
      }
    }
    
    console.error('Error validando token:', error)
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 401 || error.response?.status === 403) {
        // Token inválido o expirado
        return null
      }
    }
    return null
  }
}
