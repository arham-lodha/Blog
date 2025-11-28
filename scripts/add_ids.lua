function Header(el)
  if el.identifier == "" then
    -- Simple slugification
    local text = pandoc.utils.stringify(el)
    el.identifier = text:lower():gsub("%s+", "-"):gsub("[^%w-]", "")
  end
  return el
end
