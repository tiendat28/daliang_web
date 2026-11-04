import client from '@/core/api/client'

export const getDispatchDashboard = params => client.get('/dispatch/dashboard', { params })
export const getTrips = params => client.get('/dispatch/trips', { params })
export const createTrip = data => client.post('/dispatch/trips', data)
export const assignTrip = (id, data) => client.post(`/dispatch/trips/${id}/assign`, data)
export const updateTripStatus = (id, data) => client.post(`/dispatch/trips/${id}/status`, data)

export const getVehicles = () => client.get('/dispatch/vehicles')
export const createVehicle = data => client.post('/dispatch/vehicles', data)

export const getDrivers = () => client.get('/dispatch/drivers')
export const createDriver = data => client.post('/dispatch/drivers', data)
