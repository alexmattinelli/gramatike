// Profile page logic with Alpine.js

function profileApp() {
    return {
        user: null,
        posts: [],
        editMode: false,
        form: { name: '', bio: '', avatar: '' },
        loading: false,

        /**
         * Initialize the profile page
         */
        async init() {
            await this.loadUser();
            await this.loadUserPosts();
            
            // Initialize form with user data
            if (this.user) {
                this.form = {
                    name: this.user.name || '',
                    bio: this.user.bio || '',
                    avatar: this.user.avatar || ''
                };
            }
        },

        /**
         * Load current user
         */
        async loadUser() {
            try {
                const res = await api.get('/api/users/me');
                this.user = res.user;
            } catch (error) {
                console.error('Error loading user:', error);
                window.location.href = '/login';
            }
        },

        /**
         * Load user's posts
         */
        async loadUserPosts() {
            try {
                const res = await api.get('/api/posts');
                // Filter to only show current user's posts
                this.posts = res.posts.filter(p => p.user_id === this.user.id);
            } catch (error) {
                console.error('Error loading posts:', error);
            }
        },

        /**
         * Update user profile
         */
        async updateProfile() {
            this.loading = true;
            try {
                const res = await api.patch('/api/users/me', this.form);
                this.user = res.user;
                this.editMode = false;
                alert('Perfil atualizado com sucesso!');
            } catch (error) {
                console.error('Error updating profile:', error);
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
        },

        /**
         * Format date
         */
        formatDate(date) {
            const d = new Date(date);
            return d.toLocaleDateString('pt-BR');
        }
    };
}
