# Database Normalization Update Summary

## Changes Made

### 1. New Table Created

**customers** table:
```sql
CREATE TABLE customers (
    customer_email VARCHAR(100) PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### 2. Schema Updates

#### feedback table
- **Before**: Stored `customer_name` and `customer_email` redundantly
- **After**: Only stores `customer_email` as foreign key
- **Foreign Key**: `customer_email` → `customers(customer_email)` ON DELETE SET NULL

#### ideas table
- **Before**: No customer tracking
- **After**: Added `customer_email` column as foreign key
- **Foreign Key**: `customer_email` → `customers(customer_email)` ON DELETE SET NULL

#### innovative_ideas table
- **Before**: Stored `customer_name` and `customer_email` redundantly
- **After**: Only stores `customer_email` as foreign key
- **Foreign Key**: `customer_email` → `customers(customer_email)` ON DELETE SET NULL

### 3. Updated Functions

#### New Function
- `register_customer(customer_email, customer_name)`: Registers or updates customer (uses UPSERT)

#### Modified Functions
- `save_feedback()`: Now registers customer first, then saves feedback with only customer_email
- `get_feedback()`: Uses LEFT JOIN to retrieve customer_name from customers table
- `save_idea()`: Now accepts customer_email and customer_name parameters
- `get_ideas()`: Uses LEFT JOIN to retrieve customer_name from customers table
- `save_innovative_idea()`: Now registers customer first, then saves with only customer_email
- `get_all_innovative_ideas()`: Uses LEFT JOIN to retrieve customer_name from customers table

### 4. Benefits of Normalization

✅ **Eliminates Data Redundancy**: Customer name stored once, not repeated in every record
✅ **Data Consistency**: Updating customer name updates everywhere automatically
✅ **Referential Integrity**: Foreign keys ensure valid customer references
✅ **Storage Efficiency**: Reduces database size for large datasets
✅ **Better Tracking**: Can now track all activities per customer

### 5. Entity Relationship Diagram

```
┌─────────────────────┐
│     CUSTOMERS       │
│─────────────────────│
│ customer_email (PK) │◄─────┐
│ customer_name       │      │
│ created_at          │      │
└─────────────────────┘      │
                             │ FK
                             │
┌─────────────────────┐      │
│     FEEDBACK        │      │
│─────────────────────│      │
│ id (PK)             │      │
│ product             │      │
│ feature             │      │
│ subfeature          │      │
│ feedback_text       │      │
│ urgency             │      │
│ customer_email (FK) │──────┤
│ created_at          │      │
└─────────────────────┘      │
                             │
┌─────────────────────┐      │
│       IDEAS         │      │
│─────────────────────│      │
│ id (PK)             │      │
│ feature             │      │
│ subfeature          │      │
│ idea_text           │      │
│ thumbs_up           │      │
│ thumbs_down         │      │
│ customer_email (FK) │──────┤
│ created_at          │      │
└─────────────────────┘      │
                             │
┌─────────────────────┐      │
│ INNOVATIVE_IDEAS    │      │
│─────────────────────│      │
│ id (PK)             │      │
│ customer_email (FK) │──────┘
│ idea_text           │
│ thumbs_up           │
│ thumbs_down         │
│ approved            │
│ created_at          │
└─────────────────────┘
```

## Migration Instructions

### Step 1: Backup Your Database
```bash
pg_dump feedback_db > backup_before_normalization.sql
```

### Step 2: Run Migration Script
```bash
python migrate_to_normalized_schema.py
```

This script will:
1. Create customers table
2. Extract unique customers from existing feedback and innovative_ideas
3. Add customer_email column to ideas table
4. Add foreign key constraints
5. Verify the migration

### Step 3: Test the Application
```bash
streamlit run main.py
```

Test all features:
- Submit feedback
- Submit ideas
- View owner dashboard
- Check if customer names display correctly

### Step 4: Optional Cleanup (After Testing)
Once you verify everything works, you can drop redundant columns:

```sql
ALTER TABLE feedback DROP COLUMN IF EXISTS customer_name;
ALTER TABLE innovative_ideas DROP COLUMN IF EXISTS customer_name;
```

### Step 5: Add Performance Indexes
```sql
CREATE INDEX idx_feedback_customer ON feedback(customer_email);
CREATE INDEX idx_ideas_customer ON ideas(customer_email);
CREATE INDEX idx_innovative_ideas_customer ON innovative_ideas(customer_email);
```

## Code Usage Examples

### Saving Feedback (Automatic Customer Registration)
```python
save_feedback(
    product="Footwear",
    feature="Comfort & Fit",
    subfeature="Cushioning",
    feedback_text="Great cushioning!",
    urgency="No Need Improvement",
    customer_name="John Doe",
    customer_email="john@example.com"
)
# Automatically registers customer if new, then saves feedback
```

### Retrieving Feedback with Customer Names
```python
feedback_list = get_feedback(limit=100)
for fb in feedback_list:
    print(f"{fb['customer_name']}: {fb['feedback_text']}")
# customer_name is retrieved via JOIN from customers table
```

### Saving Ideas
```python
save_idea(
    feature="Durability",
    subfeature="Material Strength",
    idea_text="Use reinforced stitching",
    customer_email="john@example.com",
    customer_name="John Doe"
)
# Registers customer and links idea to customer_email
```

## Rollback Plan (If Needed)

If something goes wrong, restore from backup:

```bash
# Drop the database
dropdb feedback_db

# Recreate it
createdb feedback_db

# Restore from backup
psql feedback_db < backup_before_normalization.sql
```

## Notes

- **ON DELETE SET NULL**: If a customer is deleted, their feedback/ideas remain but customer_email becomes NULL
- **UPSERT Logic**: `register_customer()` uses `ON CONFLICT DO UPDATE` to handle duplicate emails
- **Backward Compatibility**: Old code still works during transition (redundant columns not dropped automatically)
- **No Data Loss**: Migration preserves all existing data

## Verification Queries

Check normalization success:

```sql
-- Count customers
SELECT COUNT(*) FROM customers;

-- Check feedback with customer names
SELECT f.id, c.customer_name, f.feedback_text 
FROM feedback f
LEFT JOIN customers c ON f.customer_email = c.customer_email
LIMIT 10;

-- Check ideas with customer names
SELECT i.id, c.customer_name, i.idea_text 
FROM ideas i
LEFT JOIN customers c ON i.customer_email = c.customer_email
LIMIT 10;

-- Find orphaned records (should be empty if migration successful)
SELECT * FROM feedback 
WHERE customer_email IS NOT NULL 
  AND customer_email NOT IN (SELECT customer_email FROM customers);
```

## Summary

✅ Database normalized with customers table
✅ Foreign key relationships established
✅ All CRUD functions updated
✅ Migration script provided
✅ Backward compatible during transition
✅ No data loss
