// Admin dashboard logic with Alpine.js

function adminApp() {
    return {
        user: null,
        stats: {
            users: 0,
            posts: 0,
            comments: 0,
            likes: 0
        },
        loading: false,

        /**
         * Initialize the admin dashboard
         */
        async init() {
            await this.loadUser();
            await this.loadStats();
        },

        /**
         * Load current user
         */
        async loadUser() {
            try {
                const res = await api.get('/api/users/me');
                this.user = res.user;
                
                // Check if user is admin
                if (!this.user.is_admin) {
                    alert('Acesso negado. Você não tem permissão para acessar esta página.');
                    window.location.href = '/feed';
                }
            } catch (error) {
                console.error('Error loading user:', error);
                window.location.href = '/login';
            }
        },

        /**
         * Load dashboard statistics
         */
        async loadStats() {
            this.loading = true;
            try {
                const res = await api.get('/api/admin/stats');
                this.stats = res.stats;
            } catch (error) {
                console.error('Error loading stats:', error);
                alert(error.message);
            } finally {
                this.loading = false;
            }
        },

        /**
         * Logout
         */
        async logout() {
            try {
                await api.post('/api/auth/logout');
                window.location.href = '/login';
            } catch (error) {
                console.error('Error logging out:', error);
                window.location.href = '/login';
            }
        }
    };
}
