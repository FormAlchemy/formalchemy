function(doc) { 
   if (doc.doc_type == "Pet") 
    emit(doc._id, doc); 
}

