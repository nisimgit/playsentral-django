import json

from django.db.models import Avg
from django.shortcuts import render
from rest_framework import status
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
import requests

from gs_django_app.models import Game, Rating, Post, Comment, Company, Series, PostResponse
from gs_django_app.serializers import GameSerializer, RatingSerializer, CommentSerializer, \
    UserSerializer, PostSerializer, ResponseSerializer

JOKES_API_URL = 'https://v2.jokeapi.dev/joke/Any?safe-mode'


# # For all relevant views, I may yet choose to allow superusers to get a list of
# # all instances but other users to get only a list of instances with is_deleted=False


@api_view(['GET'])
def jokes(request):
    response = requests.get(JOKES_API_URL)
    jokeData = json.loads(response.content)
    return Response(jokeData)


@api_view(['GET', 'PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def current_user(request):
    if request.method == 'GET':
        data = {
            'username': request.user.username,
            'userId': request.user.id
        }
        return Response(data)

    if request.method == 'PUT':
        user = User.objects.get(pk=request.user.id)
        user['first_name'] = request.data.first_name
        user['last_name'] = request.data.last_name


@api_view(['GET', 'POST'])
def games(request):
    if request.method == 'GET':
        game_objects = Game.objects.filter(is_deleted=False)

        if 'searchValue' in request.GET and request.GET['searchValue']:
            game_objects = game_objects.filter(name__icontains=request.GET['searchValue'])

        serializer = GameSerializer(game_objects, many=True)
        return Response(serializer.data)

    # # Other method/s will require superuser credentials

    elif not request.user.is_superuser:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    elif request.method == 'POST':
        serializer = GameSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([BasicAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def game_details(request, pk):
    try:
        game = Game.objects.get(pk=pk)
    except Game.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':

        def get_genre():
            return f"{game.genre_1}-{game.genre_2}" if game.genre_2 else game.genre_1

        ret_data = {
            "id": game.id,
            "name": game.name,
            "publisher": game.publisher.name,
            "developer": game.developer.name,
            "series": game.series.name if game.series else "",
            "release_year": game.release_year,
            "picture_url": game.picture_url,
            "genre": get_genre(),
        }
        return Response(ret_data)

    # # Other method/s will require superuser credentials

    elif not request.user.is_superuser:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    elif request.method == 'PUT':
        serializer = GameSerializer(game, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        game.is_deleted = True
        game.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def game_ratings(request, pk):
    if request.method == 'GET':
        ratings = Rating.objects.filter(game_id=pk)

        def get_avg_rating():
            avg = ratings.aggregate(Avg('score')).get('score__avg')
            if avg:
                return ratings.aggregate(Avg('score')).get('score__avg')
            else:
                return 0

        def get_user_rating():
            user_ratings = ratings.filter(user_id=request.user.id)
            if len(user_ratings) == 1:
                return ratings.get(user_id=request.user.id)
            # if len(ratings) > 1:
            #    pass

        avg_rating = get_avg_rating()
        user_rating_score = get_user_rating().score if get_user_rating() else 0
        user_rating_id = get_user_rating().id if get_user_rating() else 0

        ret_data = {
            'avg_rating': avg_rating,
            'user_rating_score': user_rating_score,
            'user_rating_id': user_rating_id
        }
        return Response(ret_data)

    # # Other method/s will require for the user to be a registered user (or superuser, who is a reg. user)

    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        if not request.data['rating'].isdigit():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if int(request.data['rating']) > 10:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        Rating.objects.create(
            user_id=request.user.id,
            game_id=request.data['game'],
            score=request.data['rating'])
        return Response(status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
def rating_details(request, pk):
    try:
        rating = Rating.objects.get(pk=pk)
    except Rating.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = RatingSerializer(rating)
        return Response(serializer.data)

    # # Other method/s will require for the user to be the original user.

    elif (not request.user.is_superuser) and (request.user != rating.user):
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    elif request.method == 'PUT':
        rating.score = request.data['rating']
        rating.game_id = request.data['game']
        rating.user_id = request.user.id
        rating.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
        # serializer = RatingSerializer(rating_obj, data=request.data)
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        rating.is_deleted = True
        rating.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@authentication_classes([BasicAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def game_posts(request, pk):
    if request.method == 'GET':
        posts = Post.objects.filter(is_deleted=False, game_id=pk)
        post_list = []
        for post in posts:
            post_responses = PostResponse.objects.filter(post_id=post.id)

            def get_user_response():
                try:
                    user_post_response = post_responses.get(user_id=request.user.id)
                except PostResponse.DoesNotExist:
                    return ''
                return user_post_response.response

            # print('Post responses: ', post_responses)
            # user_post_response = post_responses.filter(user_id=request.user.id)
            # print('User post response: ', user_post_response)

            post_list.append(
                {
                    'post_id': post.id,
                    'username': post.user.username,
                    'user_response': get_user_response(),
                    'likes': post_responses.filter(response='like').count(),
                    'dislikes': post_responses.filter(response='dislike').count(),
                    'text': post.text
                }
            )
        return Response(post_list, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        Post.objects.create(
            user_id=request.user.id,
            game_id=request.data['game'],
            text=request.data['text'])
        return Response(status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([BasicAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def post_details(request, pk):
    try:
        post = Post.objects.get(pk=pk)
        print(post.text)
    except Post.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PostSerializer(post)
        return Response(serializer.data)

    # # Other method/s will require for the user to be the original user or superuser.

    elif (not request.user.is_superuser) and (request.user != post.user):
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    elif request.method == 'PUT':
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        post.is_deleted = True
        post.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def post_responses(request):
    responses = PostResponse.objects.filter(is_deleted=False)

    if request.method == 'GET':
        serializer = ResponseSerializer(responses, many=True)
        print(serializer.data)
        return Response(serializer.data)

    # # Other method/s will require for the user to be a registered user (or superuser, who is a reg. user)

    elif not request.user.is_authenticated:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    elif request.method == 'POST':
        game_responses = responses.filter(post__game__id=request.data['game'], user_id=request.user.id)
        for game_response in game_responses:
            if game_response.post_id == request.data['post']:
                game_response.response = request.data['response']
                game_response.save()
                return Response(status=status.HTTP_204_NO_CONTENT)

        if Post.objects.filter(id=request.data['post']) and request.data['response']:
            PostResponse.objects.create(
                user_id=request.user.id,
                response=request.data['response'],
                post_id=request.data['post']
            )
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def response_edit(request, pk):
    try:
        response = PostResponse.objects.get(pk=pk)
    except Post.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ResponseSerializer(response)
        return Response(serializer.data)

    elif request.method == 'DELETE':
        response.is_deleted = True
        response.save()

    elif request.method == 'PUT':
        serializer = ResponseSerializer(response, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def post_comments(request, pk):
    # if request.method == 'GET':
    # comments = Comment.objects.filter(is_deleted=False, post_id=post_id)
    # serializer = CommentSerializer(comments, many=True)
    # return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'GET':
        comments = Comment.objects.filter(is_deleted=False, post_id=pk)
        comment_list = []
        for comment in comments:
            comment_list.append(
                {
                    'comment_id': comment.id,
                    'username': comment.user.username,
                    'text': comment.text
                }
            )
        return Response(comment_list, status=status.HTTP_200_OK)

    # # Other method/s will require for the user to be a registered user (or superuser, who is a reg. user)

    # elif not request.user.is_authenticated:
    #     return Response(status=status.HTTP_401_UNAUTHORIZED)
    #
    # elif request.method == 'POST':
    #     serializer = CommentSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET', 'PUT', 'DELETE'])
# def comment_details(request, pk):
#     try:
#         instance = Comment.objects.get(pk=pk)
#     except Comment.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)
#
#     if request.method == 'GET':
#         serializer = CommentSerializer(instance)
#         return Response(serializer.data)
#
#     # # Other method/s will require for the user to be the original user or superuser.
#
#     elif (not request.user.is_superuser) and (request.user != instance.user):
#         return Response(status=status.HTTP_401_UNAUTHORIZED)
#
#     elif request.method == 'PUT':
#         serializer = CommentSerializer(instance, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     elif request.method == 'DELETE':
#         instance.is_deleted = True
#         return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def signup(request):
    User.objects.create_user(
        username=request.data['username'],
        first_name=request.data['first_name'],
        last_name=request.data['last_name'],
        email=request.data['email'],
        password=request.data['password'])
    return Response(status=status.HTTP_201_CREATED)
