class CreateFeedsTagsJoinTable < ActiveRecord::Migration
  def change
    create_table :feeds_tags, id: false do |t|
      t.references :feed
      t.references :tag
    end
    add_index :feeds_tags, :feed_id
    add_index :feeds_tags, :tag_id
  end
end
