class CreateQandAs < ActiveRecord::Migration
  def change
    create_table :qand_as do |t|
      t.text :question
      t.text :answer

      t.timestamps
    end
  end
end
