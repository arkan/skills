-- Convert Obsidian callout blockquotes to Typst callout() blocks.
-- Supported markers: [!NOTE], [!WARNING], [!CAUTION], [!IMPORTANT],
-- [!SUCCESS], [!DONE], and [!DECISION].

local meta = {}
local brand = "neutral"

local labels = {
  note = "Note",
  warning = "Attention",
  caution = "Attention",
  important = "Important",
  success = "Succes",
  done = "Succes",
  decision = "Decision",
}

local tones = {
  note = "neutral",
  warning = "warning",
  caution = "danger",
  important = "warning",
  success = "success",
  done = "success",
  decision = "neutral",
}

local function meta_string(value, fallback)
  if not value then
    return fallback
  end

  return pandoc.utils.stringify(value)
end

local function typst_string(value)
  value = value:gsub("\\", "\\\\")
  value = value:gsub('"', '\\"')
  return '"' .. value .. '"'
end

local function parse_marker(block)
  if not block or (block.t ~= "Para" and block.t ~= "Plain") then
    return nil
  end

  local text = pandoc.utils.stringify(block)
  local kind, title = text:match("^%s*%[!([%w_-]+)%][%+%-]?%s*(.-)%s*$")

  if not kind then
    return nil
  end

  kind = kind:lower()

  if not labels[kind] then
    return nil
  end

  if title == "" then
    title = labels[kind]
  end

  return {
    kind = kind,
    title = title,
    tone = tones[kind] or "neutral",
  }
end

local function split_first_block(block)
  if not block or (block.t ~= "Para" and block.t ~= "Plain") then
    return nil
  end

  local before_break = pandoc.List()
  local after_break = pandoc.List()
  local found_break = false

  for _, inline in ipairs(block.content) do
    if not found_break and (inline.t == "SoftBreak" or inline.t == "LineBreak") then
      found_break = true
    elseif found_break then
      after_break:insert(inline)
    else
      before_break:insert(inline)
    end
  end

  local marker_block = block

  if found_break then
    marker_block = pandoc.Plain(before_break)
  end

  local marker = parse_marker(marker_block)

  if not marker then
    return nil
  end

  return {
    marker = marker,
    body_prefix = after_break,
  }
end

local function blocks_to_typst(blocks)
  return pandoc.write(pandoc.Pandoc(blocks, meta), "typst")
end

local function convert_callout(block)
  local parsed = split_first_block(block.content[1])

  if not parsed then
    return nil
  end

  local body = pandoc.List()

  if #parsed.body_prefix > 0 then
    body:insert(pandoc.Para(parsed.body_prefix))
  end

  for index = 2, #block.content do
    body:insert(block.content[index])
  end

  local body_typst = blocks_to_typst(body)
  local raw = "#callout("
    .. typst_string(parsed.marker.title)
    .. ", [\n"
    .. body_typst
    .. "\n], tone: "
    .. typst_string(parsed.marker.tone)
    .. ", brand: "
    .. typst_string(brand)
    .. ")"

  return pandoc.RawBlock("typst", raw)
end

function Pandoc(doc)
  meta = doc.meta
  brand = meta_string(doc.meta.brand, "neutral")

  return doc:walk({
    BlockQuote = convert_callout,
  })
end
