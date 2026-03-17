"""
Database helper methods - Add these to your existing database.py
"""
from datetime import datetime, timedelta

class Database:
    # ... existing code ...
    def get_user(self, user_id):
    """Get user by ID"""
    return self.db.users.find_one({"user_id": user_id})
    # ===== FRIEND SYSTEM =====
    def get_friends(self, user_id):
        """Get user's friends list."""
        user = self.get_user(user_id)
        return user.get('friends', []) if user else []
    
    def are_friends(self, user_id1, user_id2):
        """Check if two users are friends."""
        friends = self.get_friends(user_id1)
        return user_id2 in friends
    
    def create_friend_request(self, from_user, to_user):
        """Create a friend request."""
        self.db.friend_requests.insert_one({
            'from_user': from_user,
            'to_user': to_user,
            'status': 'pending',
            'created_at': datetime.now()
        })
    
    def get_friend_requests(self, user_id):
        """Get pending friend requests for user."""
        return list(self.db.friend_requests.find({
            'to_user': user_id,
            'status': 'pending'
        }))
    
    def has_pending_request(self, from_user, to_user):
        """Check if request already exists."""
        return self.db.friend_requests.find_one({
            'from_user': from_user,
            'to_user': to_user,
            'status': 'pending'
        }) is not None
    
    # ===== RATINGS SYSTEM =====
    def add_rating(self, rating_data):
        """Add a rating."""
        self.db.ratings.insert_one(rating_data)
    
    def get_ratings_received(self, user_id):
        """Get ratings received by user."""
        return list(self.db.ratings.find({'to_user': user_id}))
    
    def get_ratings_given(self, user_id):
        """Get ratings given by user."""
        return list(self.db.ratings.find({'from_user': user_id}))
    
    def get_rating(self, from_user, to_user):
        """Get specific rating."""
        return self.db.ratings.find_one({
            'from_user': from_user,
            'to_user': to_user
        })
    
    # ===== GARDEN SYSTEM =====
    def get_garden(self, user_id):
        """Get user's garden."""
        garden = self.db.gardens.find_one({'user_id': user_id})
        if not garden:
            garden = {'user_id': user_id, 'plants': [], 'size': 3}
            self.db.gardens.insert_one(garden)
        return garden
    
    def update_plant(self, user_id, plant_index, updates):
        """Update a specific plant."""
        self.db.gardens.update_one(
            {'user_id': user_id},
            {'$set': {f'plants.{plant_index}': updates}}
        )
    
    # ===== COOKING SYSTEM =====
    def get_stove(self, user_id):
        """Get user's stove."""
        return self.db.stoves.find_one({'user_id': user_id})
    
    def set_stove(self, user_id, stove_data):
        """Set/create stove."""
        self.db.stoves.update_one(
            {'user_id': user_id},
            {'$set': stove_data},
            upsert=True
        )
    
    def update_stove(self, user_id, updates):
        """Update stove."""
        self.db.stoves.update_one(
            {'user_id': user_id},
            updates,
            upsert=True
        )
    
    # ===== FACTORY SYSTEM =====
    def get_factory(self, user_id):
        """Get user's factory."""
        return self.db.factories.find_one({'user_id': user_id})
    
    def create_factory(self, user_id, factory_data):
        """Create new factory."""
        factory_data['user_id'] = user_id
        self.db.factories.insert_one(factory_data)
    
    def get_factory_type(self, user_id):
        """Get factory type info."""
        from modules.factory.factory import FACTORY_TYPES
        factory = self.get_factory(user_id)
        if not factory:
            return None
        return FACTORY_TYPES.get(factory.get('type', 'small'))
    
    def add_factory_worker(self, user_id, worker):
        """Add worker to factory."""
        self.db.factories.update_one(
            {'user_id': user_id},
            {'$push': {'workers': worker}}
        )
    
    def add_factory_production(self, user_id, production):
        """Add production task."""
        self.db.factories.update_one(
            {'user_id': user_id},
            {'$push': {'active_production': production}}
        )
    
    def remove_factory_production(self, user_id, product_id):
        """Remove production task."""
        self.db.factories.update_one(
            {'user_id': user_id},
            {'$pull': {'active_production': {'product_id': product_id}}}
        )
    
    def add_to_factory_storage(self, user_id, item, quantity):
        """Add item to factory storage."""
        self.db.factories.update_one(
            {'user_id': user_id},
            {'$inc': {f'storage.{item}': quantity}}
        )
    
    def remove_from_factory_storage(self, user_id, item, quantity):
        """Remove from factory storage."""
        self.db.factories.update_one(
            {'user_id': user_id},
            {'$inc': {f'storage.{item}': -quantity}}
        )
    
    # ===== MARKET SYSTEM =====
    def get_market_stand(self, user_id):
        """Get user's market stand."""
        return self.db.market_stands.find_one({'user_id': user_id})
    
    def create_market_stand(self, user_id):
        """Create new market stand."""
        stand = {
            'user_id': user_id,
            'items': [],
            'total_sales': 0,
            'total_revenue': 0,
            'created_at': datetime.now()
        }
        self.db.market_stands.insert_one(stand)
        return stand
    
    def list_item_on_stand(self, user_id, item):
        """List item on stand."""
        self.db.market_stands.update_one(
            {'user_id': user_id},
            {'$push': {'items': item}}
        )
    
    def remove_from_stand(self, user_id, item_id):
        """Remove item from stand."""
        self.db.market_stands.update_one(
            {'user_id': user_id},
            {'$pull': {'items': {'item_id': item_id}}}
        )
    
    # ===== PROFILE SYSTEM =====
    def get_users_with_locations(self):
        """Get all users who have set locations."""
        return list(self.db.users.find({'location': {'$exists': True}}))
    
    # ===== WAIFU SYSTEM =====
    def get_waifu_collection(self, user_id):
        """Get user's waifu collection."""
        user = self.get_user(user_id)
        return user.get('waifus', []) if user else []
    
    def add_waifu_to_collection(self, user_id, waifu):
        """Add waifu to collection."""
        self.db.users.update_one(
            {'user_id': user_id},
            {'$push': {'waifus': waifu}}
        )
    
    # ===== ADMIN STATS =====
    def count_users(self):
        """Count total users."""
        return self.db.users.count_documents({})
    
    def get_total_money(self):
        """Get total money in economy."""
        pipeline = [
            {'$group': {'_id': None, 'total': {'$sum': '$money'}}}
        ]
        result = list(self.db.users.aggregate(pipeline))
        return result[0]['total'] if result else 0
    
    def get_active_today(self):
        """Get users active today."""
        today = datetime.now() - timedelta(days=1)
        return self.db.users.count_documents({
            'last_active': {'$gte': today}
        })
    
    def ban_user(self, user_id, reason, banned_by):
        """Ban a user."""
        self.db.bans.insert_one({
            'user_id': user_id,
            'reason': reason,
            'banned_by': banned_by,
            'banned_at': datetime.now()
        })
        self.db.users.update_one(
            {'user_id': user_id},
            {'$set': {'banned': True}}
        )
    
    # ===== TRANSACTIONS =====
    def add_transaction(self, user_id, transaction):
        """Add transaction record."""
        self.db.transactions.insert_one({
            'user_id': user_id,
            **transaction
        })
    
    def get_transactions(self, user_id, limit=10):
        """Get recent transactions."""
        return list(self.db.transactions.find(
            {'user_id': user_id}
        ).sort('timestamp', -1).limit(limit))
    
    # ===== INTERACTIONS =====
    def record_interaction(self, user_id, target_id, action):
        """Record social interaction."""
        self.db.interactions.insert_one({
            'from_user': user_id,
            'to_user': target_id,
            'action': action,
            'timestamp': datetime.now()
        })
    
    def get_last_interaction(self, user_id, action):
        """Get last time user performed action."""
        interaction = self.db.interactions.find_one({
            'from_user': user_id,
            'action': action
        }, sort=[('timestamp', -1)])
        return interaction['timestamp'] if interaction else None
    
    def update_relationship_score(self, user_id, target_id, change):
        """Update relationship score between users."""
        self.db.relationships.update_one(
            {'user1': min(user_id, target_id), 'user2': max(user_id, target_id)},
            {'$inc': {'score': change}},
            upsert=True
    )

    def get_top_users(self, sort_by: str, limit: int = 10):
        """Get top users by criteria."""
        try:
            return list(self.db.users.find(
                {}, 
                {'user_id': 1, 'username': 1, sort_by: 1, 'level': 1, 'money': 1, 'bank': 1}
            ).sort(sort_by, -1).limit(limit))
        except Exception as e:
            print(f"Error in get_top_users: {e}")
            return []

    def get_user_rank(self, user_id: int, sort_by: str):
        """Get user's rank for a criteria."""
        try:
            user = self.get_user(user_id)
            if not user or sort_by not in user:
                return None
            higher = self.db.users.count_documents({sort_by: {'$gt': user[sort_by]}})
            return higher + 1
        except Exception as e:
            print(f"Error in get_user_rank: {e}")
            return None

    def get_all_families(self):
        """Get all families."""
        try:
            return list(self.db.families.find({}))
        except Exception as e:
            print(f"Error in get_all_families: {e}")
            return 
            []
"""
Add this at the bottom of your existing database.py file
"""

# Create global db instance
db = Database()

