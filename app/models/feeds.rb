class Feeds < ActiveRecord::Base
  attr_accessible :name

  has_many :posts
  has_many :tags
end
