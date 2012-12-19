class Post < ActiveRecord::Base
  attr_accessible :author, :title, :description

  has_many :feeds
  has_and_belongs_to_many :tags
end
