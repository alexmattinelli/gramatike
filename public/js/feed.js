// Feed page logic with Alpine.js

function feedApp() {
    return {
        user: null,
        posts: [],
        newPost: { content: '', image: null },
        loading: false,

        /**
         * Initialize the feed
         */
        async init() {
            await this.loadUser();
            await this.loadPosts();
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
                // Redirect to login if not authenticated
                window.location.href = '/login';
            }
        },

        /**
         * Load posts feed
         */
        async loadPosts() {
            try {
                const res = await api.get('/api/posts');
                this.posts = res.posts;
            } catch (error) {
                console.error('Error loading posts:', error);
            }
        },

        /**
         * Create a new post
         */
        async createPost() {
            if (!this.newPost.content.trim()) return;

            this.loading = true;
            try {
                const res = await api.post('/api/posts', this.newPost);
                this.posts.unshift(res.post);
                this.newPost = { content: '', image: null };
            } catch (error) {
                console.error('Error creating post:', error);
                alert(error.message);
            } finally {
                this.loading = false;
            }
        },

        /**
         * Toggle like on a post
         */
        async toggleLike(post) {
            try {
                await api.post(`/api/posts/${post.id}/like`);
                post.user_liked = !post.user_liked;
                post.likes_count = (post.likes_count || 0) + (post.user_liked ? 1 : -1);
            } catch (error) {
                console.error('Error toggling like:', error);
                alert(error.message);
            }
        },

        /**
         * Handle image upload
         */
        handleImageUpload(event) {
            const file = event.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = (e) => {
                this.newPost.image = e.target.result;
            };
            reader.readAsDataURL(file);
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
                // Redirect anyway
                window.location.href = '/login';
            }
        },

        /**
         * Format date
         */
        formatDate(date) {
            const d = new Date(date);
            const now = new Date();
            const diff = now - d;
            const seconds = Math.floor(diff / 1000);
            const minutes = Math.floor(seconds / 60);
            const hours = Math.floor(minutes / 60);
            const days = Math.floor(hours / 24);

            if (days > 7) {
                return d.toLocaleDateString('pt-BR');
            } else if (days > 0) {
                return `${days}d atrás`;
            } else if (hours > 0) {
                return `${hours}h atrás`;
            } else if (minutes > 0) {
                return `${minutes}min atrás`;
            } else {
                return 'agora';
            }
        }
    };
}
