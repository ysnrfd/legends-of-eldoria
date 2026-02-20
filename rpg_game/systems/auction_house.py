"""
Auction House System - Player-to-player trading with bidding

Author: YSNRFD
Version: 1.0.0
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, TYPE_CHECKING
from enum import Enum
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from core.engine import Rarity, colored_text, format_number

if TYPE_CHECKING:
    from core.character import Character
    from core.items import Item


class AuctionStatus(Enum):
    """Status of an auction listing"""
    ACTIVE = "active"
    SOLD = "sold"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


@dataclass
class AuctionListing:
    """A single auction listing"""
    id: str
    seller_id: str
    seller_name: str
    item_id: str
    item_name: str
    item_rarity: str
    quantity: int
    starting_bid: int
    buyout_price: Optional[int] = None
    current_bid: int = 0
    current_bidder_id: Optional[str] = None
    current_bidder_name: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    duration: int = 86400  # 24 hours in seconds
    status: AuctionStatus = AuctionStatus.ACTIVE
    final_price: Optional[int] = None
    bids_history: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def time_remaining(self) -> int:
        """Get seconds remaining"""
        if self.status != AuctionStatus.ACTIVE:
            return 0
        
        elapsed = time.time() - self.created_at
        remaining = self.duration - elapsed
        return max(0, int(remaining))
    
    @property
    def is_expired(self) -> bool:
        """Check if auction has expired"""
        return self.time_remaining <= 0 and self.status == AuctionStatus.ACTIVE
    
    def place_bid(self, bidder: 'Character', amount: int) -> Tuple[bool, str]:
        """Place a bid on this auction"""
        if self.status != AuctionStatus.ACTIVE:
            return False, "Auction is not active."
        
        if self.is_expired:
            return False, "Auction has expired."
        
        if bidder.id == self.seller_id:
            return False, "Cannot bid on your own auction."
        
        # Check minimum bid
        min_bid = self.current_bid + 1 if self.current_bid > 0 else self.starting_bid
        if amount < min_bid:
            return False, f"Bid must be at least {min_bid} gold."
        
        # Check if buyout
        if self.buyout_price and amount >= self.buyout_price:
            return self.buyout(bidder)
        
        # Record previous bidder refund
        if self.current_bidder_id and self.current_bid > 0:
            self.bids_history.append({
                "bidder_id": self.current_bidder_id,
                "bidder_name": self.current_bidder_name,
                "amount": self.current_bid,
                "time": time.time(),
                "outbid": True
            })
        
        # Place new bid
        self.current_bid = amount
        self.current_bidder_id = bidder.id
        self.current_bidder_name = bidder.name
        
        self.bids_history.append({
            "bidder_id": bidder.id,
            "bidder_name": bidder.name,
            "amount": amount,
            "time": time.time(),
            "outbid": False
        })
        
        return True, f"Bid placed: {amount} gold on {self.item_name}"
    
    def buyout(self, buyer: 'Character') -> Tuple[bool, str]:
        """Buyout the auction immediately"""
        if self.status != AuctionStatus.ACTIVE:
            return False, "Auction is not active."
        
        if not self.buyout_price:
            return False, "No buyout price set."
        
        # Refund previous bidder if any
        if self.current_bidder_id and self.current_bid > 0:
            self.bids_history.append({
                "bidder_id": self.current_bidder_id,
                "bidder_name": self.current_bidder_name,
                "amount": self.current_bid,
                "time": time.time(),
                "outbid": True,
                "refunded": True
            })
        
        # Complete sale
        self.current_bidder_id = buyer.id
        self.current_bidder_name = buyer.name
        self.current_bid = self.buyout_price
        self.final_price = self.buyout_price
        self.status = AuctionStatus.SOLD
        
        return True, f"Buyout successful! You won {self.item_name} for {self.buyout_price} gold!"
    
    def cancel(self, character_id: str) -> Tuple[bool, str]:
        """Cancel the auction (only seller can cancel)"""
        if self.status != AuctionStatus.ACTIVE:
            return False, "Cannot cancel inactive auction."
        
        if character_id != self.seller_id:
            return False, "Only the seller can cancel."
        
        # Refund current bidder if any
        if self.current_bidder_id and self.current_bid > 0:
            self.bids_history.append({
                "bidder_id": self.current_bidder_id,
                "bidder_name": self.current_bidder_name,
                "amount": self.current_bid,
                "time": time.time(),
                "cancelled": True,
                "refunded": True
            })
        
        self.status = AuctionStatus.CANCELLED
        return True, "Auction cancelled."
    
    def finalize(self) -> Tuple[bool, str]:
        """Finalize expired auction"""
        if self.status != AuctionStatus.ACTIVE:
            return False, "Auction already finalized."
        
        if not self.is_expired:
            return False, "Auction has not expired yet."
        
        if self.current_bidder_id:
            self.status = AuctionStatus.SOLD
            self.final_price = self.current_bid
            return True, f"Auction sold to {self.current_bidder_name} for {self.current_bid} gold!"
        else:
            self.status = AuctionStatus.EXPIRED
            return True, "Auction expired with no bids."
    
    def get_display(self) -> str:
        """Get formatted auction display"""
        rarity_color = getattr(Rarity, self.item_rarity, Rarity.COMMON).color
        
        # Time formatting
        remaining = self.time_remaining
        if remaining > 3600:
            time_str = f"{remaining // 3600}h {(remaining % 3600) // 60}m"
        elif remaining > 60:
            time_str = f"{remaining // 60}m {remaining % 60}s"
        else:
            time_str = f"{remaining}s"
        
        lines = [
            f"\n{'='*60}",
            f"Auction: {rarity_color}{self.item_name}\033[0m x{self.quantity}",
            f"{'='*60}",
            f"Seller: {self.seller_name}",
            f"Status: {self.status.value.title()}",
        ]
        
        if self.status == AuctionStatus.ACTIVE:
            lines.append(f"Time Remaining: {time_str}")
            lines.append(f"Starting Bid: {format_number(self.starting_bid)} gold")
            
            if self.current_bid > 0:
                lines.append(f"Current Bid: {format_number(self.current_bid)} gold by {self.current_bidder_name}")
            else:
                lines.append("No bids yet")
            
            if self.buyout_price:
                lines.append(f"Buyout: {format_number(self.buyout_price)} gold")
        
        elif self.status == AuctionStatus.SOLD:
            lines.append(f"Final Price: {format_number(self.final_price)} gold")
            lines.append(f"Winner: {self.current_bidder_name}")
        
        lines.append(f"\nTotal Bids: {len(self.bids_history)}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "seller_id": self.seller_id,
            "seller_name": self.seller_name,
            "item_id": self.item_id,
            "item_name": self.item_name,
            "item_rarity": self.item_rarity,
            "quantity": self.quantity,
            "starting_bid": self.starting_bid,
            "buyout_price": self.buyout_price,
            "current_bid": self.current_bid,
            "current_bidder_id": self.current_bidder_id,
            "current_bidder_name": self.current_bidder_name,
            "created_at": self.created_at,
            "duration": self.duration,
            "status": self.status.value,
            "final_price": self.final_price,
            "bids_history": self.bids_history
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AuctionListing':
        return cls(
            id=data["id"],
            seller_id=data["seller_id"],
            seller_name=data["seller_name"],
            item_id=data["item_id"],
            item_name=data["item_name"],
            item_rarity=data["item_rarity"],
            quantity=data["quantity"],
            starting_bid=data["starting_bid"],
            buyout_price=data.get("buyout_price"),
            current_bid=data.get("current_bid", 0),
            current_bidder_id=data.get("current_bidder_id"),
            current_bidder_name=data.get("current_bidder_name"),
            created_at=data["created_at"],
            duration=data.get("duration", 86400),
            status=AuctionStatus(data.get("status", "active")),
            final_price=data.get("final_price"),
            bids_history=data.get("bids_history", [])
        )


class AuctionHouse:
    """Manages the auction house"""
    
    AUCTION_FEE_PERCENT = 0.05  # 5% fee on successful sales
    
    def __init__(self):
        self.listings: Dict[str, AuctionListing] = {}
        self.sold_history: List[AuctionListing] = []  # Recently sold
        self.total_volume: int = 0  # Total gold traded
        self.total_listings: int = 0
    
    def create_listing(self, seller: 'Character', item: 'Item', 
                      starting_bid: int, buyout_price: Optional[int] = None,
                      duration_hours: int = 24) -> Tuple[bool, str, Optional[AuctionListing]]:
        """Create a new auction listing"""
        # Validate prices
        if starting_bid < 1:
            return False, "Starting bid must be at least 1 gold.", None
        
        if buyout_price and buyout_price <= starting_bid:
            return False, "Buyout price must be higher than starting bid.", None
        
        # Check if seller has the item
        if not seller.inventory.has_item(item.name, item.quantity):
            return False, "You don't have that item.", None
        
        # Remove item from seller inventory
        success, removed_item = seller.inventory.remove_item(item.name, item.quantity)
        if not success:
            return False, "Failed to remove item from inventory.", None
        
        # Create listing
        import hashlib
        listing_id = hashlib.md5(f"{seller.id}{item.name}{time.time()}".encode()).hexdigest()[:12]
        
        listing = AuctionListing(
            id=listing_id,
            seller_id=seller.id,
            seller_name=seller.name,
            item_id=item.name.lower().replace(" ", "_"),
            item_name=item.name,
            item_rarity=item.rarity.name,
            quantity=item.quantity,
            starting_bid=starting_bid,
            buyout_price=buyout_price,
            duration=duration_hours * 3600
        )
        
        self.listings[listing_id] = listing
        self.total_listings += 1
        
        return True, f"Listed {item.name} for auction! Listing ID: {listing_id}", listing
    
    def get_listing(self, listing_id: str) -> Optional[AuctionListing]:
        """Get a specific listing"""
        return self.listings.get(listing_id)
    
    def get_active_listings(self, category: Optional[str] = None, 
                           rarity: Optional[Rarity] = None,
                           seller: Optional[str] = None) -> List[AuctionListing]:
        """Get active listings with optional filters"""
        active = [l for l in self.listings.values() if l.status == AuctionStatus.ACTIVE]
        
        if category:
            active = [l for l in active if category.lower() in l.item_name.lower()]
        
        if rarity:
            active = [l for l in active if l.item_rarity == rarity.name]
        
        if seller:
            active = [l for l in active if l.seller_name.lower() == seller.lower()]
        
        return sorted(active, key=lambda x: x.created_at, reverse=True)
    
    def search_listings(self, query: str) -> List[AuctionListing]:
        """Search listings by name"""
        query = query.lower()
        return [l for l in self.listings.values() 
                if l.status == AuctionStatus.ACTIVE and query in l.item_name.lower()]
    
    def place_bid(self, bidder: 'Character', listing_id: str, amount: int) -> Tuple[bool, str]:
        """Place a bid on a listing"""
        listing = self.listings.get(listing_id)
        if not listing:
            return False, "Listing not found."
        
        # Check if bidder has enough gold
        if bidder.inventory.gold < amount:
            return False, "You don't have enough gold."
        
        # Place bid
        success, message = listing.place_bid(bidder, amount)
        
        if success:
            # Deduct gold from bidder
            bidder.inventory.gold -= amount
            
            # Refund previous bidder if any
            if len(listing.bids_history) > 1:
                prev_bid = listing.bids_history[-2]
                if prev_bid.get("bidder_id") and not prev_bid.get("outbid"):
                    # Previous bidder gets refund
                    pass  # Would need to add gold to that character
        
        return success, message
    
    def buyout(self, buyer: 'Character', listing_id: str) -> Tuple[bool, str]:
        """Buyout a listing"""
        listing = self.listings.get(listing_id)
        if not listing:
            return False, "Listing not found."
        
        if not listing.buyout_price:
            return False, "No buyout price set."
        
        if buyer.inventory.gold < listing.buyout_price:
            return False, "You don't have enough gold."
        
        # Deduct gold
        buyer.inventory.gold -= listing.buyout_price
        
        # Complete sale
        success, message = listing.buyout(buyer)
        
        if success:
            self._complete_sale(listing)
        
        return success, message
    
    def cancel_listing(self, character_id: str, listing_id: str) -> Tuple[bool, str]:
        """Cancel a listing"""
        listing = self.listings.get(listing_id)
        if not listing:
            return False, "Listing not found."
        
        return listing.cancel(character_id)
    
    def finalize_expired(self) -> List[AuctionListing]:
        """Finalize all expired auctions"""
        finalized = []
        
        for listing in self.listings.values():
            if listing.status == AuctionStatus.ACTIVE and listing.is_expired:
                success, message = listing.finalize()
                if success:
                    finalized.append(listing)
                    if listing.status == AuctionStatus.SOLD:
                        self._complete_sale(listing)
        
        return finalized
    
    def _complete_sale(self, listing: AuctionListing):
        """Complete a sale and transfer funds"""
        if listing.final_price:
            # Calculate fee
            fee = int(listing.final_price * self.AUCTION_FEE_PERCENT)
            seller_profit = listing.final_price - fee
            
            self.total_volume += listing.final_price
            
            # Move to history
            self.sold_history.append(listing)
            if len(self.sold_history) > 100:  # Keep last 100
                self.sold_history.pop(0)
            
            # Remove from active
            if listing.id in self.listings:
                del self.listings[listing.id]
    
    def get_market_statistics(self) -> Dict[str, Any]:
        """Get auction house statistics"""
        active_count = len([l for l in self.listings.values() if l.status == AuctionStatus.ACTIVE])
        sold_count = len([l for l in self.listings.values() if l.status == AuctionStatus.SOLD])
        
        # Calculate average prices by rarity
        rarity_prices: Dict[str, List[int]] = {}
        for listing in self.listings.values():
            if listing.current_bid > 0:
                if listing.item_rarity not in rarity_prices:
                    rarity_prices[listing.item_rarity] = []
                rarity_prices[listing.item_rarity].append(listing.current_bid)
        
        avg_prices = {r: sum(prices) // len(prices) if prices else 0 
                     for r, prices in rarity_prices.items()}
        
        return {
            "active_listings": active_count,
            "sold_today": sold_count,
            "total_volume": self.total_volume,
            "total_listings_ever": self.total_listings,
            "average_prices": avg_prices
        }
    
    def get_display(self) -> str:
        """Get auction house display"""
        stats = self.get_market_statistics()
        
        lines = [
            f"\n{'='*60}",
            "AUCTION HOUSE",
            f"{'='*60}",
            f"Active Listings: {stats['active_listings']}",
            f"Total Volume: {format_number(stats['total_volume'])} gold",
            f"",
            "Average Prices by Rarity:"
        ]
        
        for rarity, price in stats['average_prices'].items():
            rarity_color = getattr(Rarity, rarity, Rarity.COMMON).color
            lines.append(f"  {rarity_color}{rarity}\033[0m: {format_number(price)} gold")
        
        # Show featured listings (highest bids)
        active = self.get_active_listings()
        if active:
            lines.append(f"\nFeatured Listings:")
            for listing in sorted(active, key=lambda x: x.current_bid, reverse=True)[:5]:
                rarity_color = getattr(Rarity, listing.item_rarity, Rarity.COMMON).color
                bid_str = f"{format_number(listing.current_bid)}" if listing.current_bid > 0 else "No bids"
                lines.append(f"  {rarity_color}{listing.item_name}\033[0m - {bid_str} gold")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        return {
            "listings": {k: v.to_dict() for k, v in self.listings.items()},
            "sold_history": [l.to_dict() for l in self.sold_history],
            "total_volume": self.total_volume,
            "total_listings": self.total_listings
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AuctionHouse':
        ah = cls()
        ah.listings = {k: AuctionListing.from_dict(v) for k, v in data.get("listings", {}).items()}
        ah.sold_history = [AuctionListing.from_dict(l) for l in data.get("sold_history", [])]
        ah.total_volume = data.get("total_volume", 0)
        ah.total_listings = data.get("total_listings", 0)
        return ah


print("Auction house system loaded successfully!")
