from django.shortcuts import render

from django.views.generic import View
from django.http import HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist

from stage.models import Stage, Block
from pdm.settings import STATIC_URL

import json

# Create your views here.
def play_game(request):
    context = {'logged_in': True}
    stage = None

    if u'stageid' in request.GET:
        stage_id = request.GET[u'stageid']
    
        try:
            stage = Stage.objects.get(pk=stage_id)
        except ObjectDoesNotExist:
            stage = Stage.objects.default_stage()
            if int(stage_id) != 0:
                context['error'] = "Stage not found! Loading default stage"
        except Exception as e: # Shouldn't be reached
            print e
            raise

        context['stageid'] = stage.pk
        context['rating'] = stage.rating
        context['name'] = stage.name
        context['owner'] = stage.owner
        if request.user.is_authenticated() and stage.owner == request.user.username:
            context['correct_owner'] = True

    return render(request, 'game/game.html', context)

def load_stage(request, stage_id = 0):
    context = {}
    stage = None
    try:
        stage = Stage.objects.get(pk=stage_id)
    except ObjectDoesNotExist:
        stage = Stage.objects.default_stage()
        if int(stage_id) != 0:
            context['error'] = "Stage not found! Loading default stage"
    except Exception as e: # Shouldn't be reached
        print e
        raise

    Block.objects.build_default() # JIC

    response_data = {
        'width' : stage.width,
        'height': stage.height,
        'spsize': 32,
        'start' : {'x': 0, 'y': 0}, # Only one start point
        'end'   : [],
        'blocks': [],
        'enemies':[],
    }

    assets = {
        'start': Block.objects.get(ID=Block.startID).sprite,
        'goal':  Block.objects.get(ID=Block.endID).sprite,
        'block': Block.objects.get(ID='#').sprite,
        'enemy': Block.objects.get(ID='x').sprite, }
    response_data['assets'] = {key: STATIC_URL + assets[key] for key in assets}

    x, y = 0, 0
    for c in stage.data:
        if c == '\r': 
            pass
        elif c == '\n':
            x, y = 0, y+1
        else:
            try:
                block = Block.objects.get(ID=c)
                if block.ID == Block.startID:
                    response_data['start'] = {'x': x, 'y': y}
                elif block.ID == Block.endID:
                    response_data['end'].append({'x': x, 'y': y})
                elif block.ID == '#':
                    response_data['blocks'].append({'x': x, 'y': y})
                elif block.ID == 'x':
                    response_data['enemies'].append({'x': x, 'y': y})
            except ObjectDoesNotExist:
                pass
            x += 1

    context['data'] = json.dumps(response_data)

    return render(request, 'game/game.js', context, content_type = 'text/javascript')

def get_stage(request):
    context = {}
    if request.user.is_authenticated():
        context['logged_in'] = True
        stages = Stage.objects.filter(owner = request.user.username)
        if len(stages):
            context['stages'] = stages
            sorted(context['stages'], key=lambda st: st.rating)
            context['message'] = "Saved Stages"
        else:
            context['message'] = "You have no saved stages."
    else:
        context['message'] = 'You are not logged in!'

    totalCount = Stage.objects.count()
    context['recentstages'] = []

    amountAdded = 0
    currentStage = totalCount
    while amountAdded < min(7, totalCount):
        if currentStage < 0:
            break

        if Stage.objects.filter(pk = currentStage).exists():
            context['recentstages'].append(Stage.objects.get(pk = currentStage))
            amountAdded = amountAdded + 1

        currentStage = currentStage - 1

    context['username'] = request.user.username 

    return render(request, 'game/play.html', context)
