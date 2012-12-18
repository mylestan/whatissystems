class Posts < ActiveRecord::Base
  attr_accessible :author, :title

  # has_many :tags
  has_many :feeds
end
