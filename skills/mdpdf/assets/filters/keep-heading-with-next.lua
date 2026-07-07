-- Keep section headings visually attached to their first meaningful block.
-- This filter targets Typst output and wraps Heading levels 1-3 plus the
-- following block in a sticky Typst block.

local function is_target_heading(block)
  return block.t == "Header" and block.level >= 1 and block.level <= 3
end

local function is_meaningful(block)
  return block and block.t ~= "Null"
end

local function is_safe_to_serialize(block)
  return block.t ~= "CodeBlock" and block.t ~= "RawBlock"
end

local function to_typst(blocks, meta)
  return pandoc.write(pandoc.Pandoc(blocks, meta), "typst")
end

function Pandoc(doc)
  local output = pandoc.List()
  local blocks = doc.blocks
  local index = 1

  while index <= #blocks do
    local current = blocks[index]

    if is_target_heading(current) then
      local next_index = index + 1

      while next_index <= #blocks and not is_meaningful(blocks[next_index]) do
        next_index = next_index + 1
      end

      local next_block = blocks[next_index]

      if next_block and not is_target_heading(next_block) and is_safe_to_serialize(next_block) then
        local wrapped_typst = to_typst({ current, next_block }, doc.meta)

        output:insert(pandoc.RawBlock("typst", "#block(sticky: true)[\n" .. wrapped_typst .. "\n]"))

        index = next_index + 1
      else
        output:insert(current)
        index = index + 1
      end
    else
      output:insert(current)
      index = index + 1
    end
  end

  doc.blocks = output
  return doc
end
