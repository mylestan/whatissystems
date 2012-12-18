class RemoveColumnFromPosts < ActiveRecord::Migration
  def up
    remove_column :posts, :content
  end

  def down
    add_column :posts, :content, :text
  end
end
