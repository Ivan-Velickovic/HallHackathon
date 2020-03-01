const apiURL = 'http://localhost:5000';

export function fetchAPI(url, method, data) {
    const headers = {}
    if (localStorage.getItem('token')) {
        headers.Authorization = getToken()
    }
    if (data) {
        headers['Content-Type'] = 'application/json'
    }
        return (
            fetch(apiURL + url, {
                method: method, // or 'PUT'
                body: JSON.stringify(data), // data can be `string` or {object}!
                headers: headers
            })
            .then(r => {
                console.log(r)//eslint-disable-line
                const j = r.json()
                j.status = r.status
                return j
            })
        )
}

export function getToken() {
    return localStorage.getItem('token')
}

export function setToken(token) {
    return localStorage.setItem('token', token)
}

export function removeToken() {
    return localStorage.removeItem('token')
}

export function isAuthenticated() {
    const localStorageToken = getToken()
    // const tokenIsValid = false
    // TODO: will need to check if user is authenticated (checking token validity on backend) as well as
    // their authorization level (another check on the backend). Best to use Promise.all ?

    if (!localStorageToken) {
        return false
    }

    // TODO: only authorized when permission is not 0
    // TODO: need to check on backend if token is valid as well.

    // return tokenIsValid
    return true // TODO: for debugging purposes user is always authenticated.
}

export function isAdmin() {
    return false
}

export { apiURL };
