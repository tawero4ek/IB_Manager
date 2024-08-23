------------------------------------------{ Salavat }------------------------------------------
--| Модуль информационной безопасности [версия: 1.0] |-----------------------------------------
-----------------------------------------------------------------------------------------------
--| Скорректированно: 2019.08.21 |-------------------------------------------------------------
---| 2023.05.02 --steam |----------------------------------------------------------------------
-- Декларативная часть:
updateInterval = 20 -- период создания Syslog файлов, сек
maxCategory = 999 -- номер категории, выше которого события не фиксируются

-- =============================== Обработка событий ИБ =======================================
local qtyEv = 0
-- Функция сохраняет на диск список событий + заполняют глобальные сигналы для их передачи на БД.
local function getEvent(arg)
local logMessage= ''
-- Получаем текущее время
	local dt = os.time()
-- Запрашиваем список событий от текущего времени и depth секунд назад.
	local events = Core.getEvents(dt-arg.depth, dt)
-- steam если свежих событий нет или сервер в резерве выходим из функции
	if #events == 0 or Core['@RESERVED'] then return end
	-- Начинаем сканировать
    for i=1,#events  do 
-- выбираем и записываем в файл только события ИБ (с категорией ниже 1000) steam
		if events[i].category > 0 and events[i].category <= maxCategory then 
			--	local textMes = ''			-- Шаблон сообщения
 			local eventID= ''			-- ID события для ИБ
 			--	local codeSonata= ''			-- Код события из Сонаты
 			local severity= ''			-- Серьезность сообщения]]
			-- записывем для передачи в лог
			local c_evTimeStamp= os.date('%Y.%m.%d %H:%M:%S.%3N', events[i].dt).."\t" -- Время регистрации события
			if events[i].application then --steam
				eventNode, eventApp = events[i].application:match('([%w_]+)%.([%w_]+)') --имя Узла, имя Приложения
 			else eventNode= '' -- нет данных
			 	eventApp = ''
 			end

		--[[-- Выполняем сканирование TableEvent ----------------------------
 				Запоминаем переменные полученные из таблицы
 		--------------------------------------------------------------------]]
 			for _,v in ipairs(TableEvent) do
				if events[i].msg then
					if events[i].msg:find(v.TextMes) then
	--					textMes		= v.TextMes		не используется
						eventID		= v.EventID		
	--					codeSonata	= v.CodeSonata		не используется
						severity	= v.Severity	
						break
					end
				end	
			end

		--[[-- Заполнение таблицы Meta -----------------------------------
 				Сканирование переменной meta и занесение значений в таблицу
 		--------------------------------------------------------------------]]
 			local metaTable = {}													-- таблица для заполнения данных из Meta
 			if events[i].meta then 	
				for k, v in events[i].meta:gmatch("(%w+)=([^%,]+)") do metaTable[k] = (v:sub(-1)==' ') and v:sub(1,-2) or v end
 			end
			local meta = '' 
			if  string.format("%s", events[i].meta)~= nil then meta = string.format("%s", events[i].meta) end --steam 
        	if meta:find('AO') ~=nil or meta:find('eventIB') ~=nil then qtyEv = qtyEv + 1         		
			else qtyEv = 22	  		
			end

		--[[-- Заполнение Severity -----------------------------------------
 				Получение серьезности события
 					[1=Низкая 2=Высокая]
 		--------------------------------------------------------------------]]
			local c_severity
       		local t = {['1']='Низкая', ['2']='Высокая'}
	    	if metaTable.Severity then
					c_severity= string.gsub(tostring(metaTable.Severity), "(%d)", t)	-- получаем Критичность		
			else c_severity= string.gsub(tostring(severity), "(%d)", t)	
			end

		--[[-- Заполнение таблицы EventID -----------------------------------
 				Для получения EventID сравниваем каждое сообщение с шаблоном
 		--------------------------------------------------------------------]]
			local c_evID= tostring(eventID)

		--[[-- Заполнение таблицы EventName -----------------------------------
 			 	Имя произошедшего события
 		--------------------------------------------------------------------]]
			local c_evName = events[i].msg:gsub(string.format("%s", events[i].dt), "")	

		--[[-- Заполнение таблицы UserName-----------------------------------
 				Получаем текущее имя пользователя -----
 		--------------------------------------------------------------------]]
			local c_userName = events[i].user									 
			if events[i].user == '' then c_userName = 'Система' end

		--[[--  -----------------------------------
 				Записываем IP адрес АРМ и его сетевое имя
				Присвоение адреса целевого узла (ГПА)
				Записываем IP и Имя рабочего сервера
 		--------------------------------------------------------------------]]
			local c_clientAddr ='' -- ип адрес арма
			local c_armName ='' -- имя адрес арма 
			local c_targetNameRu= 'Система' -- Имя контроллера в ЧМИ, на которых нацелено событие
			local c_ipPLC= '' -- ип адрес контроллера
			local c_PLCname= '' -- имя узла контроллера
		-- определение ип адреса источника сообщения
		-- проверяем, является ли узел события клиентом
			for _,z in ipairs(Client) do 
				if eventNode == z then 
					c_clientAddr = nodes[eventNode] -- записали ип адрес арма
					c_armName = metaTable['Node'] or '' -- записали имя источника
					break		
				end
			end
			-- записываем данные сервера
			local nm= string.match(Core.getName(),'[%w_]+') -- получили имя этого сервера
			local c_ipThisNode = nodes[nm] -- записали ип адрес этого сервера
			local c_nameThisNode= nm -- записали имя этого сервера
			-- записываем данные контроллеров
			metaTable['PrefAb']= metaTable['PrefAb'] or ''
			metaTable['NameRU']= metaTable['NameRU'] or ''
			nm = (metaTable['PrefAb']:sub(-1)== '_') and metaTable['PrefAb']:sub(1,-2) or metaTable['PrefAb'] -- выделяем имя узла
			for _,z in ipairs(Target) do
				if nm == z then 
					c_targetNameRu= metaTable['NameRU'] -- записали русское имя контроллера  
					c_ipPLC= nodes[nm] or '' -- записали ип адрес контроллера
					c_PLCname= nm	-- записали имя узла контроллера				
					break	
				end	
			end			
--Core.addLogMsg("П: "..string.sub("GPA4_",1,-2)..", А: "..string.sub("GPA4_",-1), "./flevents.log")	
	
		--[[ -- Заполнение таблицы по Result
 					Результат произошедшего события (успешный или не успешный)
					[Success=Успех, Failed=Неудача]
 		--------------------------------------------------------------------]]
--			Core[arg.IBE_tab[14]]	= "Успешно"

		--[[-- Заполнение таблицы по Detail -----------------------------------
				Поле не обязательное
				На текущий момент расшифровывается статус сообщения
 		--------------------------------------------------------------------]]
			local c_state
        	local state = events[i].state
        	if state == 1 or state== 769 then c_state = "Пришло" -- 769?
			elseif state == 2 then c_state = "Квитировано"
			elseif state == 3 then c_state = "Исчезло"
			else c_state = "Снялось"
			end
--			Core[arg.IBE_tab[15]] = state --..', '..events[i].category

		-- Перечень регистрируемых параметров событий клиентского приложения -----------------------------------
--			logMessage= logMessage.."- "..Core[arg.IBE_tab[1] ].."\t"..
			logMessage= logMessage..c_evTimeStamp..c_armName..'>'..
							" SCADA-EventCategory "..events[i].category..
							";Severity="..c_severity..
							";EventID="..c_evID..
							";EventName="..c_evName..
							";UserName="..c_userName..
							";ClientAddress="..c_clientAddr..
							";ServerAddress="..c_ipThisNode..
							";ServerHostName="..c_nameThisNode..
							";TargetUserName="..c_targetNameRu..
							";TargetAddress="..c_ipPLC..
							";TargetHostName="..c_PLCname..
							";Result= Успешно"..
							";Detail="..c_state.."\n"
	  	end	
	end

	if logMessage== '' then return end -- если новых сообщений ИБ нет выходим --steam
	local fileName = "Syslog_Client"..os.date("_%Y%m%d_%H%M%S.log", dt) -- Формируем имя файла.
	local file = io.open('log/'..fileName, "w+") -- Открываем файл.
	if file == nil then -- на тот случай, если папка с логами была удалена
		os.execute("mkdir log") 
		file = io.open('log/'..fileName, "w+") 
	end	
	file:write(logMessage)
	file:close()
end

--------------------------- Получить имена узлов и их ип адреса ------------------------------------------------
local function getNodes()
	local U={}
	local apps= Core.getApps() -- получаем таблицу приложений, связанных с сервером
	for k,v in pairs(apps) do
		local n= k:match('[%w_]+')
		if U[n] == nil then U[n] = v.addrs:sub(1,v.addrs:find(':')-1) end -- отделяем от ип адреса порт  
--Core.addLogMsg("П: "..n..", А: "..U[n], "./flevents.log")
	end
	return U
end

------------------------------- проверка наличие файлов --------------------------------------------------------
local isfile = function(flname)
	local fl = assert(io.open(flname, "r"), "Файл "..flname.." не найден")
	fl:close()
end

------------------------------------- Инициализация --------------------------------------------------------------
--dofile('decode_Ansi_Utf8.lua')							-- Запускаем конвертер текста
-- Windows
--computerName 	= os.getenv("computername")				-- Получаем имя компьютера
--userName 		= os.getenv("username")					-- Получаем имя пользователя
-- Linux
--computerName 	= os.getenv("HOSTNAME")				-- Получаем имя компьютера
--userName 		= os.getenv("USER")					-- Получаем имя пользователя
isfile('InfSec/ConfigurationTab.lua')
isfile('InfSec/TableEventID.lua')	
-- Открываем файлы необходимые для работы
dofile('InfSec/ConfigurationTab.lua')			-- таблица с характеристками проекта
dofile('InfSec/TableEventID.lua')				-- открываем таблицу с идентификаторами для ИБ
--makeLogDir('./log')	-- папка для логов 
nodes= getNodes() -- получаем таблицу узлов

Core.onTimer(1, 
            updateInterval,
			getEvent,							
			{depth = updateInterval} 				-- Глубина запроса данных [s].
			 ) 
Core.waitEvents()
