from rest_framework.permissions import BasePermission
from rest_framework.generics import get_object_or_404

from board.models import Board,Card,Column
import json

class IsAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_admin:
            return True
        return False

    def has_permission(self, request, view):
        try:
            if request.user.is_admin:
                return True
            return False
        except:
            return False


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        try:
            if request.user.is_admin or obj.owner==request.user:
                return True
            return False
        except:
            return False
    
    def has_permission(self, request, view):
        if 'name' in view.__dict__ and  view.name=='Members':
            board_id=request.parser_context.get('kwargs').get('pk')
            board_instance=get_object_or_404(Board,id=board_id)
            result=self.has_object_permission(request,view,board_instance)
            return result
        
        if 'basename' in view.__dict__ and view.basename=='column':
            if view.action=='create':
                body=json.loads(request._request.body)
                board_id=body.get('board')
                board_instance=get_object_or_404(Board,id=board_id)
            else:
                column_id=request.parser_context.get('kwargs').get('pk')
                column_instance=get_object_or_404(Column,id=column_id)
            result=self.has_object_permission(request,view,board_instance if view.action=='create' else column_instance.board)
            return result

        return super().has_permission(request, view)

    

    
class IsMemberOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        try:
            if request.user.is_admin or obj.owner==request.user or request.user in obj.members.all():
                return True
            return False
        except Exception as e:
            return False
        
    def has_permission(self, request, view):
        # comment and card permission check permission check
        if 'basename' in view.__dict__ and view.basename in ['comment','card']:

            comment_generic=view.basename=='comment'
            if view.basename=='card' and view.action in ['update','partial_update','retrieve','destory']:
                navigation_id=request.parser_context.get('kwargs').get('pk')
                navigated_initial_instance=get_object_or_404(Card,id=navigation_id)
                navigated_instance=navigated_initial_instance.column
            else:
                body=json.loads(request._request.body)
                comment_generic=view.basename=='comment'
                # get card_id if comment else column_id
                navigation_id=body.get('card' if comment_generic else 'column')
                navigated_instance=get_object_or_404(Card if comment_generic else Column ,id=navigation_id)

                
            board_instance=navigated_instance.column.board if comment_generic else navigated_instance.board
            result=self.has_object_permission(request,view,board_instance)
            return result
        
        # board detail data view permission check
        if request._request.resolver_match.url_name=='board-list-detail':
            board_id=request.parser_context.get('kwargs').get('pk')
            board_instance=get_object_or_404(Board,id=board_id)
            result=self.has_object_permission(request,view,board_instance)
            return result
        
        return super().has_permission(request, view)

    