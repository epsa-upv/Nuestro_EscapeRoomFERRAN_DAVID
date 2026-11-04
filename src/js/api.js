/* EscapeHub — cliente HTTP REST
 * El contrato exacto está en doc/api_rest.md.
 * Cambiar API_BASE si David usa otro host/puerto.
 */
(function () {
  'use strict';

  const API_BASE = window.ESCAPEHUB_API_BASE || 'http://127.0.0.1:5000/api';
  let accessToken = null;

  class ApiError extends Error {
    constructor(message, status = 0, code = 'ERROR') {
      super(message);
      this.name = 'ApiError';
      this.status = status;
      this.code = code;
    }
  }

  async function request(path, options = {}) {
    const headers = { Accept: 'application/json', ...(options.headers || {}) };
    if (options.body !== undefined) headers['Content-Type'] = 'application/json';
    if (accessToken) headers.Authorization = `Bearer ${accessToken}`;

    let response;
    try {
      response = await fetch(`${API_BASE}${path}`, {
        method: options.method || 'GET',
        headers,
        body: options.body === undefined ? undefined : JSON.stringify(options.body),
        signal: options.signal
      });
    } catch (error) {
      if (error.name === 'AbortError') throw error;
      throw new ApiError('No se puede conectar con el servidor. Comprueba que Flask esté iniciado y la API disponible.', 0, 'SIN_CONEXION');
    }

    const raw = response.status === 204 ? '' : await response.text();
    let payload = null;
    if (raw) {
      try { payload = JSON.parse(raw); }
      catch { throw new ApiError('La API no devolvió JSON válido.', response.status, 'RESPUESTA_INVALIDA'); }
    }
    if (!response.ok) {
      const info = payload && payload.error;
      const message = typeof info === 'string' ? info : info?.mensaje;
      throw new ApiError(message || `Solicitud rechazada (HTTP ${response.status}).`, response.status, info?.codigo || 'HTTP_ERROR');
    }
    return payload;
  }

  window.EscapeAPI = Object.freeze({
    get base() { return API_BASE; },
    setToken(token) { accessToken = token || null; },
    clearToken() { accessToken = null; },
    register: body => request('/auth/registro', { method: 'POST', body }),
    login: body => request('/auth/login', { method: 'POST', body }),
    rooms: () => request('/salas'),
    room: id => request(`/salas/${encodeURIComponent(id)}`),
    addRoom: body => request('/salas', { method: 'POST', body }),
    updateRoom: (id, body) => request(`/salas/${encodeURIComponent(id)}`, { method: 'PUT', body }),
    deleteRoom: id => request(`/salas/${encodeURIComponent(id)}`, { method: 'DELETE' }),
    sessions: (filters = {}) => {
      const qs = new URLSearchParams();
      for (const [key, value] of Object.entries(filters)) {
        if (value !== undefined && value !== null && String(value) !== '') qs.set(key, String(value));
      }
      return request(`/sesiones${qs.size ? `?${qs}` : ''}`);
    },
    addSession: body => request('/sesiones', { method: 'POST', body }),
    reservations: () => request('/reservas'),
    book: body => request('/reservas', { method: 'POST', body }),
    cancel: id => request(`/reservas/${encodeURIComponent(id)}`, { method: 'PUT', body: { estado: 'CANCELADA' } }),
    // Retos configurados por administrador (las soluciones nunca se exponen)
    challenges: roomId => request(`/salas/${encodeURIComponent(roomId)}/retos`),
    addChallenge: (roomId, body) => request(`/salas/${encodeURIComponent(roomId)}/retos`, { method: 'POST', body }),
    updateChallenge: (id, body) => request(`/retos/${encodeURIComponent(id)}`, { method: 'PUT', body }),
    deleteChallenge: id => request(`/retos/${encodeURIComponent(id)}`, { method: 'DELETE' }),
    addHint: (challengeId, body) => request(`/retos/${encodeURIComponent(challengeId)}/pistas`, { method: 'POST', body }),
    addObject: (roomId, body) => request(`/salas/${encodeURIComponent(roomId)}/objetos`, { method: 'POST', body }),
    addDependency: (id, body) => request(`/retos/${encodeURIComponent(id)}/dependencias`, { method: 'POST', body }),
    // Partidas: solo el titular o administrador puede consultarlas
    games: () => request('/partidas'),
    game: id => request(`/partidas/${encodeURIComponent(id)}`),
    createGame: reservationId => request('/partidas', { method: 'POST', body: { reserva_id: reservationId } }),
    startGame: id => request(`/partidas/${encodeURIComponent(id)}/iniciar`, { method: 'POST', body: {} }),
    submitAnswer: (gameId, challengeId, respuesta) => request(`/partidas/${encodeURIComponent(gameId)}/retos/${encodeURIComponent(challengeId)}/intentos`, { method: 'POST', body: { respuesta } }),
    useObject: (gameId, challengeId, objectId) => request(`/partidas/${encodeURIComponent(gameId)}/retos/${encodeURIComponent(challengeId)}/usar-objeto`, { method: 'POST', body: { objeto_id: objectId } }),
    useHint: (gameId, challengeId, hintId) => request(`/partidas/${encodeURIComponent(gameId)}/retos/${encodeURIComponent(challengeId)}/pistas/${encodeURIComponent(hintId)}/usar`, { method: 'POST', body: {} }),
    collectObject: (gameId, objectId) => request(`/partidas/${encodeURIComponent(gameId)}/objetos/${encodeURIComponent(objectId)}/recoger`, { method: 'POST', body: {} }),
    results: () => request('/resultados'),
    addResult: body => request('/resultados', { method: 'POST', body }),
    ApiError
  });
})();
