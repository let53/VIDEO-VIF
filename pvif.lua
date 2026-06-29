local component = require("component")
local term = require("term")
local os = require("os")
local gpu = component.gpu

local args = { ... }
local filename = args[1] or "/home/myvideo.vif"

local file, err = io.open(filename, "r")
if not file then
  print("Ошибка открытия файла: " .. tostring(err))
  return
end

-- Читаем заголовок (W, H, FPS)
local header = file:read("*l")
local w, h, fps = header:match("(%d+),(%d+),(%d+)")
w, h, fps = tonumber(w), tonumber(h), tonumber(fps)

-- Настраиваем экран
term.clear()
gpu.setResolution(w, h)
local delay = 1 / fps

-- Цикл воспроизведения кадров
for line in file:lines() do
  local x = 1
  local y = 1
  
  -- Быстрый рендеринг строки кадра
  for hex_color in line:gmatch("%S+") do
    local color = tonumber(hex_color, 16)
    gpu.setBackground(color)
    gpu.set(x, y, " ") -- Рисуем цветной пиксель пробелом
    
    x = x + 1
    if x > w then
      x = 1
      y = y + 1
    end
  end
  os.sleep(delay) -- Задержка между кадрами
end

file:close()
gpu.setBackground(0x000000)
term.clear()
print("Воспроизведение завершено!")
