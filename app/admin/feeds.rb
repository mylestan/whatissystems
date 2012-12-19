ActiveAdmin.register Feed do
  filter :name
  filter :id

  config.sort_order = "id_asc"
end
