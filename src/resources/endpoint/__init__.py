class EndPoint(object):
    @staticmethod
    def do_operation(segment, id, request, ume_db, app_db):
        if(segment == 'login'):
            import src.resources.endpoint.login as RequestedResource
            return RequestedResource.login(request,
                                           ume_db)
        elif(segment == 'refresh'):
            import src.resources.endpoint.refresh as RequestedResource
            return RequestedResource.refresh()
        elif(segment == 'po'):
            import src.resources.endpoint.po as RequestedResource
            return RequestedResource.getAll(request, app_db, ume_db)

        elif(segment == 'filter'):
            import src.resources.endpoint.filter as RequestedResource
            return RequestedResource.filterItems(request, app_db, ume_db)

        elif(segment == 'getPoAll'):
            import src.resources.endpoint.po as RequestedResource
            return RequestedResource.get_po_all(request, app_db)

        elif(segment == 'main'):
            import src.resources.endpoint.main as RequestedResource
            return RequestedResource.getAll(request,
                                            ume_db,
                                            app_db)
        elif(segment == 'vendor'):
            import src.resources.endpoint.vendor as RequestedResource
            return RequestedResource.get_single(request,
                                                app_db,
                                                ume_db)
        elif(segment == 'vendorlist'):
            import src.resources.endpoint.vendor as RequestedResource
            return RequestedResource.get_list(request,
                                              app_db,
                                              ume_db)
        elif(segment == 'vRevPerUpdate'):
            import src.resources.endpoint.vendor as RequestedResource
            return RequestedResource.perUpdate(request,
                                               app_db,
                                               ume_db)
        elif(segment == 'vRevUpdate'):
            import src.resources.endpoint.vendor as RequestedResource
            return RequestedResource.revUpdate(request,
                                               app_db,
                                               ume_db)
        elif(segment == 'anounce'):
            import src.resources.endpoint.anounce as RequestedResource
            return RequestedResource.get_anounce(request,
                                                 app_db,
                                                 ume_db)
        elif(segment == 'anounceadd'):
            import src.resources.endpoint.anounce as RequestedResource
            return RequestedResource.send_anounce(request,
                                                  app_db,
                                                  ume_db)
        elif(segment == 'anouncedel'):
            import src.resources.endpoint.anounce as RequestedResource
            return RequestedResource.del_anounce(request,
                                                 app_db,
                                                 ume_db)

        elif(segment == 'changestatus'):
            import src.resources.endpoint.statu as RequestedResource
            return RequestedResource.update_statu(request,
                                                  app_db,
                                                  ume_db)

        elif(segment == 'getSasAttach'):
            import src.resources.endpoint.po as RequestedResource
            return RequestedResource.get_attach(request,
                                                app_db,
                                                ume_db)

        elif(segment == 'getVenAttach'):
            import src.resources.endpoint.vendor as RequestedResource
            return RequestedResource.get_attach(request,
                                                app_db,
                                                ume_db)

        elif(segment == 'delVenAttach'):
            import src.resources.endpoint.vendor as RequestedResource
            return RequestedResource.del_attach(request,
                                                app_db,
                                                ume_db)

        elif(segment == 'postVenAttach'):
            import src.resources.endpoint.vendor as RequestedResource
            return RequestedResource.post_attach(request,
                                                 app_db,
                                                 ume_db)

        elif(segment == 'postapprove'):
            import src.resources.endpoint.vendor as RequestedResource
            return RequestedResource.post_approve(request,
                                                  app_db,
                                                  ume_db)

        elif(segment == 'sendPass'):
            import src.resources.endpoint.admin as RequestedResource
            return RequestedResource.sendPass(request,
                                              ume_db,
                                              app_db)

        elif(segment == 'getUsers'):
            import src.resources.endpoint.admin as RequestedResource
            return RequestedResource.getUsers(request,
                                              ume_db,
                                              app_db)

        elif(segment == 'update'):
            import src.resources.endpoint.admin as RequestedResource
            return RequestedResource.update(request,
                                            ume_db,
                                            app_db)

        elif(segment == 'delete'):
            import src.resources.endpoint.admin as RequestedResource
            return RequestedResource.delete(request,
                                            ume_db,
                                            app_db)

        elif(segment == 'forget'):
            import src.resources.endpoint.login as RequestedResource
            return RequestedResource.forget(request,
                                            ume_db)

        elif(segment == 'newpass'):
            import src.resources.endpoint.login as RequestedResource
            return RequestedResource.changePass(request,
                                                ume_db)

        elif(segment == 'getReport'):
            import src.resources.endpoint.report as RequestedResource
            return RequestedResource.get_reports(request,
                                                 app_db,
                                                 ume_db)

        elif(segment == 'findPo'):
            import src.resources.endpoint.report as RequestedResource
            return RequestedResource.find_po(request,
                                             app_db,
                                             ume_db)

        elif(segment == 'pushAttach'):
            import src.resources.endpoint.anounce as RequestedResource
            return RequestedResource.push_help_attach(request,
                                                      app_db,
                                                      ume_db)

        elif(segment == 'getHelpAtt'):
            import src.resources.endpoint.anounce as RequestedResource
            return RequestedResource.pull_help_attach(request,
                                                      app_db,
                                                      ume_db)

        elif(segment == 'delHelpAtt'):
            import src.resources.endpoint.anounce as RequestedResource
            return RequestedResource.del_help_attach(request,
                                                      app_db,
                                                      ume_db)
                                                      
