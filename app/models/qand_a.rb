class QandA < Posts
  belongs_to :posts
  attr_accessible :answer, :question
end
