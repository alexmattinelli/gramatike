// API client utilities for Gramátike v2

const api = {
    /**
     * Make a request to the API
     */
    async request(url, options = {}) {
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            credentials: 'include'
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Erro na requisição');
        }

        return response.json();
    },

    /**
     * GET request
     */
    get(url) {
        return this.request(url);
    },

    /**
     * POST request
     */
    post(url, data) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    /**
     * PATCH request
     */
    patch(url, data) {
        return this.request(url, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
    },

    /**
     * DELETE request
     */
    delete(url) {
        return this.request(url, {
            method: 'DELETE'
        });
    }
};
