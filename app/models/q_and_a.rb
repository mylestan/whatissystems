class QAndA < Posts
  belongs_to :posts
  attr_accessible :answer, :question
end
