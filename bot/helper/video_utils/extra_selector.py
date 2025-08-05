from time import time
from asyncio import Event, wait_for, TimeoutError
from bot.helper.telegram_helper.message_utils import sendMessage, editMessage, deleteMessage
from bot.helper.telegram_helper.button_build import ButtonMaker

class ExtraSelect:
    def __init__(self, listener):
        self.listener = listener
        self._is_m4a = False
        self._time = time()
        self._timeout = 30
        self._is_playlist = False
        self._main_buttons = None
        self.is_cancelled = False
        self.event = Event()
        self.streams_to_remove = []

    async def _event_handler(self):
        pfunc = partial(select_streams, obj=self)
        handler = self.listener.client.add_handler(CallbackQueryHandler(pfunc, filters=regex('^extra') & user(self.listener.user_id)), group=-1)
        try:
            await wait_for(self.event.wait(), timeout=self._timeout)
        except TimeoutError:
            await editMessage('Timed Out. Task has been cancelled!', self.listener.editable)
            self.is_cancelled = True
            self.event.set()
        finally:
            self.listener.client.remove_handler(*handler)

    async def streams_select(self, streams):
        future = self._event_handler()
        buttons = ButtonMaker()
        msg = f"<b>MERGE & REMOVE AUDIO ~ @{self.listener.message.from_user.username}</b>\n"
        msg += f"<code>{self.listener.name}</code>\n"
        msg += f"Size: <b>{self.listener.size}</b>\n\n"
        msg += "<b>Streams:</b>\n"
        for i, stream in enumerate(streams):
            stream_type = stream.get('codec_type')
            lang = stream.get('tags', {}).get('language', 'Unknown')
            if stream_type == 'video':
                msg += f"{i+1}. Video ~ {stream.get('codec_name')} ({lang}) ({stream.get('height')}p)\n"
            elif stream_type == 'audio':
                msg += f"{i+1}. Audio ~ {stream.get('codec_name')} ({lang.upper()})\n"
            elif stream_type == 'subtitle':
                msg += f"{i+1}. Subtitle ~ {stream.get('codec_name')} ({lang.upper()})\n"
            buttons.ibutton(str(i+1), f"extra merge_rmaudio {i}")

        buttons.ibutton("Select All", "extra merge_rmaudio all")
        buttons.ibutton("Reset", "extra merge_rmaudio reset")
        buttons.ibutton("Continue", "extra merge_rmaudio continue")
        buttons.ibutton("Cancel", "extra cancel")

        self._main_buttons = buttons.build_menu(2)

        await sendMessage(self.listener.message, msg, self._main_buttons)
        await wrap_future(future)
        return self.streams_to_remove

async def select_streams(client, query, obj):
    data = query.data.split()
    if data[1] == 'cancel':
        await editMessage('Task has been cancelled.', query.message)
        obj.is_cancelled = True
        obj.event.set()
    elif data[1] == 'continue':
        obj.event.set()
    elif data[1] == 'all':
        obj.streams_to_remove = list(range(len(obj.listener.executor.streams)))
        await obj.update_message()
    elif data[1] == 'reset':
        obj.streams_to_remove = []
        await obj.update_message()
    else:
        stream_index = int(data[2])
        if stream_index in obj.streams_to_remove:
            obj.streams_to_remove.remove(stream_index)
        else:
            obj.streams_to_remove.append(stream_index)
        await obj.update_message()

    obj.update_message = async def():
        msg = f"<b>MERGE & REMOVE AUDIO ~ @{obj.listener.message.from_user.username}</b>\n"
        msg += f"<code>{obj.listener.name}</code>\n"
        msg += f"Size: <b>{obj.listener.size}</b>\n\n"
        msg += "<b>Streams:</b>\n"
        for i, stream in enumerate(obj.listener.executor.streams):
            stream_type = stream.get('codec_type')
            lang = stream.get('tags', {}).get('language', 'Unknown')
            if i in obj.streams_to_remove:
                msg += "🔵 "
            if stream_type == 'video':
                msg += f"{i+1}. Video ~ {stream.get('codec_name')} ({lang}) ({stream.get('height')}p)\n"
            elif stream_type == 'audio':
                msg += f"{i+1}. Audio ~ {stream.get('codec_name')} ({lang.upper()})\n"
            elif stream_type == 'subtitle':
                msg += f"{i+1}. Subtitle ~ {stream.get('codec_name')} ({lang.upper()})\n"

        if obj.streams_to_remove:
            msg += "\n<b>To Remove:</b>\n"
            for i in obj.streams_to_remove:
                stream = obj.listener.executor.streams[i]
                stream_type = stream.get('codec_type')
                lang = stream.get('tags', {}).get('language', 'Unknown')
                if stream_type == 'video':
                    msg += f"{i+1}. Video ~ {stream.get('codec_name')} ({lang}) ({stream.get('height')}p)\n"
                elif stream_type == 'audio':
                    msg += f"{i+1}. Audio ~ {stream.get('codec_name')} ({lang.upper()})\n"
                elif stream_type == 'subtitle':
                    msg += f"{i+1}. Subtitle ~ {stream.get('codec_name')} ({lang.upper()})\n"

        time_left = obj._timeout - (time() - obj._time)
        msg += f"\n<i>Time Left: {int(time_left)}s</i>"

        await editMessage(msg, query.message, obj._main_buttons)
