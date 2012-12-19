class CreatePostsTagsJoinTable < ActiveRecord::Migration
  def change
    create_table :posts_tags, id: false do |t|
      t.references :post
      t.references :tag
    end
    add_index :posts_tags, :post_id
    add_index :posts_tags, :tag_id
  end
end
