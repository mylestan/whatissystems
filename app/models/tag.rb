class Tag < ActiveRecord::Base
  attr_accessible :name

  has_and_belongs_to_many :posts
  has_and_belongs_to_many :feeds
end
